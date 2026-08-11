"""
Knowledge Base Tools - Vector Database & RAG Implementation

This module provides ChromaDB integration for the RAG poisoning attack demonstration.
Uses sentence-transformers for free, local embeddings.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer

# ANSI color codes for visual output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class KnowledgeBase:
    """
    Vector database manager using ChromaDB with sentence-transformers embeddings.
    
    Manages both clean and poisoned documents for demonstration purposes.
    """
    
    def __init__(self, collection_name: str = "shopbot_knowledge", persist_directory: str = None):
        """
        Initialize the knowledge base.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the database
        """
        self.collection_name = collection_name
        
        # Set persist directory
        if persist_directory is None:
            persist_directory = str(Path(__file__).parent / "data" / "vector_store")
        
        self.persist_directory = persist_directory
        
        # Initialize embedding model (free, local)
        print(f"{Colors.CYAN}🔄 Loading embedding model (sentence-transformers)...{Colors.RESET}")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print(f"{Colors.GREEN}✓ Embedding model loaded{Colors.RESET}")
        
        # Initialize ChromaDB client with proper settings
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Use EphemeralClient for in-memory storage (simpler for demos)
        # Data persists during runtime but resets between runs
        self.client = chromadb.EphemeralClient()
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"{Colors.GREEN}✓ Using existing collection: {collection_name}{Colors.RESET}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "ShopBot knowledge base for RAG demo"}
            )
            print(f"{Colors.GREEN}✓ Created new collection: {collection_name}{Colors.RESET}")
    
    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        """
        Add a document to the knowledge base.
        
        Args:
            doc_id: Unique document ID
            content: Document text content
            metadata: Document metadata (source, type, is_poisoned, etc.)
        """
        # Generate embedding
        embedding = self.embedding_model.encode(content).tolist()
        
        # Add to collection
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )
        
        poison_indicator = f"{Colors.RED}⚠️  POISONED{Colors.RESET}" if metadata.get('is_poisoned') else f"{Colors.GREEN}✓{Colors.RESET}"
        print(f"  {poison_indicator} Added: {doc_id} ({metadata.get('type', 'unknown')})")
    
    def add_documents_batch(self, documents: List[Dict[str, Any]]):
        """
        Add multiple documents in batch.
        
        Args:
            documents: List of dicts with 'id', 'content', and 'metadata' keys
        """
        ids = []
        embeddings = []
        contents = []
        metadatas = []
        
        for doc in documents:
            ids.append(doc['id'])
            contents.append(doc['content'])
            metadatas.append(doc['metadata'])
            
            # Generate embedding
            embedding = self.embedding_model.encode(doc['content']).tolist()
            embeddings.append(embedding)
        
        # Add batch to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )
        
        print(f"{Colors.GREEN}✓ Added {len(documents)} documents in batch{Colors.RESET}")
    
    def search(self, query: str, n_results: int = 3, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search the knowledge base using semantic similarity.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of documents with their metadata and scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        try:
            result = self.collection.get(ids=[doc_id])
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'content': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
        except:
            pass
        return None
    
    def list_all_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the knowledge base."""
        try:
            result = self.collection.get()
            documents = []
            for i in range(len(result['ids'])):
                documents.append({
                    'id': result['ids'][i],
                    'content': result['documents'][i],
                    'metadata': result['metadatas'][i]
                })
            return documents
        except:
            return []
    
    def delete_document(self, doc_id: str):
        """Delete a document by ID."""
        self.collection.delete(ids=[doc_id])
        print(f"{Colors.YELLOW}Deleted: {doc_id}{Colors.RESET}")
    
    def clear_all(self):
        """Clear all documents from the knowledge base."""
        # Delete and recreate collection
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "ShopBot knowledge base for RAG demo"}
        )
        print(f"{Colors.YELLOW}🗑️  Cleared all documents from {self.collection_name}{Colors.RESET}")
    
    def count_documents(self) -> int:
        """Count total documents in the knowledge base."""
        return self.collection.count()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        docs = self.list_all_documents()
        
        total = len(docs)
        poisoned = sum(1 for d in docs if d['metadata'].get('is_poisoned'))
        clean = total - poisoned
        
        types = {}
        for doc in docs:
            doc_type = doc['metadata'].get('type', 'unknown')
            types[doc_type] = types.get(doc_type, 0) + 1
        
        return {
            'total_documents': total,
            'clean_documents': clean,
            'poisoned_documents': poisoned,
            'documents_by_type': types
        }


def load_documents_from_directory(directory: Path, is_poisoned: bool = False) -> List[Dict[str, Any]]:
    """
    Load all markdown documents from a directory.
    
    Args:
        directory: Path to directory containing .md files
        is_poisoned: Whether these documents are poisoned
        
    Returns:
        List of document dictionaries
    """
    documents = []
    
    if not directory.exists():
        return documents
    
    # Recursively find all .md files
    for md_file in directory.rglob("*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine document type from path
        relative_path = md_file.relative_to(directory)
        if 'product' in str(relative_path).lower():
            doc_type = 'product_doc'
        elif 'policy' in str(relative_path).lower() or 'policies' in str(relative_path).lower():
            doc_type = 'policy'
        elif 'faq' in str(relative_path).lower():
            doc_type = 'faq'
        else:
            doc_type = 'general'
        
        # Create document
        doc_id = md_file.stem.replace(' ', '_').lower()
        
        documents.append({
            'id': doc_id,
            'content': content,
            'metadata': {
                'filename': md_file.name,
                'type': doc_type,
                'is_poisoned': is_poisoned,
                'source': str(relative_path)
            }
        })
    
    return documents


def initialize_knowledge_base(kb: KnowledgeBase, clean_docs_dir: Path, poisoned_docs_dir: Path = None):
    """
    Initialize knowledge base with clean documents and optionally poisoned ones.
    
    Args:
        kb: KnowledgeBase instance
        clean_docs_dir: Directory with clean documents
        poisoned_docs_dir: Optional directory with poisoned documents
    """
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}🗄️  Initializing Knowledge Base{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")
    
    # Clear existing data
    kb.clear_all()
    
    # Load clean documents
    print(f"{Colors.GREEN}📚 Loading clean documents...{Colors.RESET}")
    clean_docs = load_documents_from_directory(clean_docs_dir, is_poisoned=False)
    if clean_docs:
        kb.add_documents_batch(clean_docs)
    else:
        print(f"{Colors.YELLOW}⚠️  No clean documents found in {clean_docs_dir}{Colors.RESET}")
    
    # Load poisoned documents if provided
    if poisoned_docs_dir and poisoned_docs_dir.exists():
        print(f"\n{Colors.RED}☠️  Loading poisoned documents (ATTACK MODE)...{Colors.RESET}")
        poisoned_docs = load_documents_from_directory(poisoned_docs_dir, is_poisoned=True)
        if poisoned_docs:
            kb.add_documents_batch(poisoned_docs)
        else:
            print(f"{Colors.YELLOW}⚠️  No poisoned documents found in {poisoned_docs_dir}{Colors.RESET}")
    
    # Print statistics
    stats = kb.get_statistics()
    print(f"\n{Colors.BOLD}📊 Knowledge Base Statistics:{Colors.RESET}")
    print(f"  Total documents: {stats['total_documents']}")
    print(f"  Clean documents: {Colors.GREEN}{stats['clean_documents']}{Colors.RESET}")
    print(f"  Poisoned documents: {Colors.RED}{stats['poisoned_documents']}{Colors.RESET}")
    print(f"  Documents by type: {stats['documents_by_type']}")
    print()
