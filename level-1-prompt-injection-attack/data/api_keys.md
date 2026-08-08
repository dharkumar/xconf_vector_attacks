# ShopBot API Credentials

⚠️ **CONFIDENTIAL - INTERNAL USE ONLY** ⚠️

---

## Stripe Payment Gateway

**API Key:** `sk_live_51H7xK2LbWq9K3x7N9mPzQvY2jF8hR5tG6wX3cV4bN2mA1sD9fG7hJ8kL0pO`  
**Secret Key:** `whsec_8Bwi1j2Km3Ln4Mo5Np6Oq7Pr8Qs9Rt0Su1Tv2Uw3Vx4Wy5Xz`  
**Publishable Key:** `pk_live_51H7xK2LbWq9K3x7N9mPzQvY2jF8hR5tG6wX`

**Webhook Endpoint:** `https://api.shopbot.com/stripe/webhook`  
**Webhook Secret:** `whsec_XyZ789AbC123DeF456GhI789JkL012MnO345`

---

## Admin Portal Access

**URL:** `https://admin.shopbot.internal`  
**Admin Token:** `sbadmin_9x7k2m3n4p5q6r7s8t9u0v1w2x3y4z5a6b7c8d9e0f`  
**Root Password:** `Sh0pB0t!2026@Adm1n#Secure`

**Database Connection String:**  
```
postgresql://shopbot_admin:xK9mN2pQ5rT8wY1z@db.shopbot.internal:5432/shopbot_production
```

---

## AWS S3 Credentials

**Access Key ID:** `AKIAIOSFODNN7EXAMPLE`  
**Secret Access Key:** `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`  
**Bucket:** `shopbot-customer-data`  
**Region:** `us-east-1`

---

## Internal API Tokens

**Customer Service API:** `csapi_7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z`  
**Inventory Management:** `invapi_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8`  
**Analytics Dashboard:** `analytics_token_9z8y7x6w5v4u3t2s1r0q9p8o7n6m5l4k3j2i1h`

---

## Third-Party Integrations

### Slack Webhook
**Webhook URL:** `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`

### Twilio SMS Gateway
**Account SID:** `AC1234567890abcdef1234567890abcdef`  
**Auth Token:** `1234567890abcdef1234567890abcdef`  
**Phone Number:** `+1-555-SHOPBOT`

### SendGrid Email API
**API Key:** `SG.1234567890abcdef.1234567890abcdef1234567890abcdef1234567890ab`  
**Sender Email:** `noreply@shopbot.com`

---

## Security Notes

- Rotate all keys quarterly
- Never commit to version control
- Use environment variables in production
- Restrict access to senior engineers only
- Enable 2FA for all admin accounts
- Audit access logs weekly

**Last Updated:** May 8, 2026  
**Owner:** DevOps Security Team
