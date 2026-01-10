# Anvil App Setup - Operational Procedure

**Document Type:** Operational Procedure  
  **Version:** 1.0  
  **Date:** December 31, 2025  
**Status:** Active  
**Related Docs:** 01_conceptual_design.md, 02_dev_policy.md, 03_dev_plan.md

---

## Purpose

This procedure defines how to set up Anvil apps for MyBizz platform development, including the Master Template, staging environment, management app, and client instances.

  **Key Principle:** Consistent setup ensures reliability and maintainability across all apps.

    ---

  ## When to Use

  - **Phase 1, Stage 1:** Setting up mybizz_core (Master Template)
  - **Phase 9:** Setting up app_mgt (MyBizz Management)
  - **Phase 10:** Setting up app_staging (Testing Environment)
  - **Client Onboarding:** Setting up each new client instance

  ---

  ## Prerequisites

  **Before starting:**
  - ✅ Anvil account created (email verified)
  - ✅ Development plan reviewed (03_dev_plan.md)
  - ✅ Naming conventions understood (05_nomenclature.md)
- ✅ Database schema available (06_database_schema.md)
- ✅ Git repository initialized (for version control)

---

## PART 1: Setting Up mybizz_core (Master Template)

### Step 1: Create New Anvil App

1. **Log into Anvil:** https://anvil.works
2. **Click "Create New App"**
3. **Select "Material Design" theme**
4. **Name the app:** `mybizz_core`
5. **Description:** "MyBizz Master Template - Core platform with all features"

### Step 2: Configure App Settings

**Navigate to:** ⚙️ Settings

**App Settings:**
- **App Name:** MyBizz Master Template
- **Subdomain:** `mybizz-core` (or similar available subdomain)
- **Package Name:** `mybizz_core`
- **Python Version:** 
  - Server: 3.10
  - Client: 3 (latest)
- **Theme:** Material Design (already selected)

**Publishing Settings:**
- ✅ Enable "Use as Dependency"
- ✅ Set visibility to "Private" (only MyBizz can access)
- **Version:** Start with v0.1.0 (development)
- **Description:** "MyBizz core platform - all features included"

**Custom Domains:**
- Not needed for Master Template (dependencies don't use custom domains)
- Will be configured for client instances only

### Step 3: Enable Required Services

**Navigate to:** ⚙️ Settings → Services

**Enable these Anvil services:**

1. **Users Service** ✅
   - Used for: Authentication, user management
   - Configure:
     - ✅ Email confirmation required
     - ✅ Password strength: Medium
     - ✅ Allow Google login: Yes (optional for clients)
     - ✅ Remember devices: 30 days

2. **Data Tables Service** ✅
   - Used for: All database storage
   - Configure:
     - Default (no special config)
     - Will create tables as development progresses

3. **Stripe Service** ✅
   - Used for: Payment processing
   - Configure:
     - **Test Mode:** Yes (during development)
     - **Live Keys:** Add later (Phase 3 when ready for real transactions)
   - API Keys:
     - Stored in Anvil Secrets (not in code)

4. **Email Service** ✅
   - Used for: Transactional emails (supplemented by Brevo)
   - Configure:
     - **From Address:** Set your verified email
     - **Reply-To:** Same as from address
   - Note: Will integrate Brevo API for bulk sending

5. **Secrets Service** ✅
   - Used for: Storing API keys, credentials
   - Configure:
     - **encryption_master_key:** Generate random 32-byte key (base64)
     - **brevo_api_key:** Add when Brevo account created
     - **dhl_api_key:** Add when DHL account created
     - **facebook_app_secret:** Add when Facebook app created
   - Security: Never log secrets, never expose client-side

### Step 4: Set Up Database Tables

**Navigate to:** 🗂 Data Tables

**Initial Core Tables** (create these first):

1. **users** (Anvil Users Service - built-in)
   - Extend with custom columns:
   - `role` (text): 'admin', 'staff', 'client'
   - `permissions` (simple object): JSON permissions
   - `last_login` (date): Track activity
   - `active` (bool): Enable/disable accounts

2. **tbl_config** (Business configuration)
   - `key` (text, unique): Configuration key
   - `value` (simple object): Configuration value
   - `category` (text): 'system', 'client', 'vertical'
   - `updated` (date): Last modified
   - `updated_by` (link to users): Who modified

3. **tbl_business_profile** (Client business info)
   - `business_name` (text): Client's business name
   - `tagline` (text): Marketing tagline
   - `logo` (media): Business logo
   - `primary_color` (text): Hex color for branding
   - `secondary_color` (text): Hex color for accents
   - `contact_email` (text): Business email
   - `contact_phone` (text): Business phone
   - `address` (simple object): Business address
   - `timezone` (text): e.g., 'Africa/Johannesburg'
   - `currency` (text): e.g., 'ZAR', 'USD'

4. **tbl_vertical_config** (Vertical selection)
   - `vertical_type` (text): 'hospitality', 'consulting', 'ecommerce', 'memberships'
   - `activated_date` (date): When selected
   - `subscription_tier` (text): 'monthly', 'annual'
   - `subscription_status` (text): 'active', 'past_due', 'cancelled'

**Additional tables created during development:**
- Reference 06_database_schema.md for complete list
- Add tables as features are built (not all upfront)

### Step 5: Create Initial Forms

**Navigate to:** 📄 Forms

**Create initial skeleton forms:**

1. **frm_startup** (Default startup form)
   - Purpose: App entry point, handles routing
   - Components: ContentPanel (will contain routing logic)

2. **frm_login** (Login form)
   - Purpose: User authentication
   - Components: TextBox (email), TextBox (password), Button (login)

3. **frm_register** (Registration form)
   - Purpose: New user signup
   - Components: TextBox (email), TextBox (password), TextBox (confirm), Button (register)

4. **frm_dashboard** (Main dashboard)
   - Purpose: Landing page after login
   - Components: ColumnPanel (sidebar), ContentPanel (main area)

**Note:** Build out forms progressively as features are developed. Don't create all forms upfront.

### Step 6: Create Server Modules

**Navigate to:** 🐍 Server Code → Add Server Module

**Create initial server modules:**

1. **sm_auth** (Authentication logic)
   ```python
   import anvil.server
   import anvil.users
   
   @anvil.server.callable
   def login_user(email, password):
       try:
           user = anvil.users.login_with_email(email, password)
           return {'success': True, 'user': user}
       except Exception as e:
           return {'success': False, 'error': str(e)}
   ```

2. **sm_config** (Configuration management)
   ```python
   import anvil.server
   from anvil.tables import app_tables
   
   @anvil.server.callable
   def get_config(key):
       try:
           row = app_tables.tbl_config.get(key=key)
           return row['value'] if row else None
       except Exception as e:
           print(f"Error getting config: {e}")
           return None
   ```

3. **sm_security** (Encryption/decryption)
   - Implement secret management
   - See 01_conceptual_design.md for encryption code

**Note:** Add server modules as needed for each feature.

### Step 7: Configure Git Integration

**Navigate to:** ⚙️ Settings → Version Control

**Option A: GitHub Integration (Recommended)**
1. **Connect to GitHub:**
   - Click "Connect to GitHub"
   - Authorize Anvil app
   - Select repository: `mybizz-platform`
   - Branch: `main` (or `master`)

2. **Commit Strategy:**
   - Commit after each feature completion
   - Use meaningful commit messages
   - Tag versions: v0.1.0, v0.2.0, v1.0.0, etc.

**Option B: Manual Git (Alternative)**
1. **Clone app using Anvil CLI**
2. **Manage via local Git**
3. **Push back to Anvil when ready**

**Recommended:** Use built-in GitHub integration for simplicity.

### Step 8: Set Up Development Workflow

**Create branches:**
- `main` - Production-ready code
- `dev` - Development integration
- `feature/feature-name` - Feature branches

**Workflow:**
1. Create feature branch from `dev`
2. Develop feature
3. Test in feature branch
4. Merge to `dev` when complete
5. Test in `dev`
6. Merge to `main` for release

---

## PART 2: Setting Up app_staging (Staging/Testing)

### Purpose
Test updates before deploying to production Master Template.

### Process

1. **Create new Anvil app:** `app_staging`
2. **Clone mybizz_core:**
   - ⚙️ Settings → Clone App
   - Select source: `mybizz_core`
   - Name: `mybizz_staging`
   - Description: "Testing environment for MyBizz updates"

3. **Configure as dependency test:**
   - Keep all settings identical to mybizz_core
   - Use TEST data (not real client data)
   - Enable all services (same as mybizz_core)

4. **Testing workflow:**
   - Make changes in mybizz_core
   - Publish to staging first
   - Test thoroughly
   - If pass: publish to production
   - If fail: fix in mybizz_core, repeat

**Key: Staging is CLONE, not separate codebase.** Changes made in mybizz_core, tested in staging.

---

## PART 3: Setting Up app_mgt (MyBizz Management)

### Purpose
MyBizz's own business operations (subscriber management, billing).

### Process

1. **Create new Anvil app:** `app_mgt`
2. **Clone mybizz_core:**
   - Source: `mybizz_core` (latest stable version)
   - Name: `mybizz_management`
   - Description: "MyBizz business operations - subscriber management"

3. **Configure for MyBizz business:**
   - **Vertical:** Memberships & Subscriptions
   - **Business Profile:** MyBizz company info
   - **Stripe:** MyBizz Stripe account (for collecting subscriptions)
   - **Brevo:** MyBizz Brevo account

4. **Customize for management:**
   - Add subscriber dashboard (list all client instances)
   - Add provisioning workflow forms
   - Add billing management
   - Add support ticket system

**Key: This is MyBizz's operational app, using own product.** (Dogfooding)

---

## PART 4: Setting Up Client Instances

### Purpose
Create isolated instance for each MyBizz subscriber.

### Prerequisites
- Client has paid subscription
- Client info collected (business name, vertical, etc.)

### Process

**Step 1: Create Anvil Account for Client**
1. **Go to Anvil.works**
2. **Create new account** using client's email (or MyBizz email like client@mybizz.com)
3. **Verify email**
4. **Log in as client account**

**Note:** MyBizz pays for Anvil subscription, not client.

**Step 2: Clone Master Template**
1. **In client's Anvil account:**
2. **Click "Create New App"**
3. **Select "Clone App"**
4. **Source:** `mybizz_core` (use sharing link from MyBizz account)
5. **Name:** `[ClientBusinessName]_mybizz`
6. **Description:** "[ClientBusinessName] business management platform"

**Step 3: Configure Dependency**
1. **⚙️ Settings → Dependencies**
2. **Add dependency:** `mybizz_core` (Published version)
3. **Version:** Latest stable (e.g., v1.0.0)
4. **Update preference:** "Notify me" (not auto-update)

**Step 4: Configure Client Settings**
1. **Custom domain:** `clientname.mybizz.app`
   - Or client's own domain (e.g., clientbusiness.com)
2. **Business profile:** Client's logo, colors, info
3. **Vertical selection:** Set in `tbl_vertical_config`
4. **Services:** All enabled (same as mybizz_core)

**Step 5: Configure Client Secrets**
1. **⚙️ Settings → Secrets**
2. **Add client's credentials:**
   - `stripe_api_key` (client's Stripe)
   - `paypal_client_id` (client's PayPal)
   - `facebook_page_token` (if using social syndication)
   - `dhl_account_number` (if using shipping)

**Note:** These are CLIENT'S credentials, not MyBizz's.

**Step 6: Initialize Data**
1. **Run setup wizard** (in client app)
2. **Client enters:**
   - Business info
   - First products/services
   - Payment gateway setup
   - Test transactions

**Step 7: Test & Verify**
1. **MyBizz tests:**
   - Login works
   - Forms load correctly
   - Vertical features display
   - Payments process (test mode)
   - Emails send

2. **If pass:** Hand off to client
3. **If fail:** Debug and re-test

**Step 8: Client Training**
1. **Provide login credentials** (admin account)
2. **Conduct training session** (video call or recorded)
3. **Provide training materials** (knowledge base articles)
4. **Set up support access** (MyBizz retains Anvil credentials)

---

## Common Setup Issues

### Issue: Services Not Enabled
**Symptom:** Features fail with "Service not available"
**Solution:** ⚙️ Settings → Services → Enable required service

### Issue: Dependency Not Found
**Symptom:** "Dependency unavailable" error
**Solution:** Ensure mybizz_core is published and set as dependency

### Issue: Database Tables Missing
**Symptom:** "Table not found" errors
**Solution:** Create tables per 06_database_schema.md

### Issue: Secrets Not Accessible
**Symptom:** `anvil.secrets.get_secret()` returns None
**Solution:** ⚙️ Settings → Secrets → Add required secrets

### Issue: Custom Domain Not Working
**Symptom:** Domain doesn't load app
**Solution:** 
1. Verify DNS records (CNAME pointing to Anvil)
2. Wait 24-48 hours for DNS propagation
3. Check Anvil custom domain configuration

---

## Quality Checklist

**Before considering setup complete:**

- [ ] App name and description set correctly
- [ ] All required services enabled
- [ ] Database tables created (core tables at minimum)
- [ ] Initial forms created
- [ ] Server modules created
- [ ] Git integration configured
- [ ] Secrets added (development keys)
- [ ] Test login works
- [ ] Test form navigation works
- [ ] Dependency configured (for client instances)
- [ ] Documentation updated

---

## Post-Setup Tasks

### For mybizz_core (Master Template):
1. **Begin Phase 1 development** (authentication, dashboard, etc.)
2. **Commit regularly** to Git
3. **Test frequently** in app_staging
4. **Publish when stable** (tag version)

### For app_mgt (Management App):
1. **Configure for MyBizz business**
2. **Set up subscriber database**
3. **Configure billing** (MyBizz Stripe)
4. **Build client provisioning workflow**

### For Client Instances:
1. **Monitor initial usage** (first 7 days)
2. **Address any issues** quickly
3. **Collect feedback**
4. **Update knowledge base** based on common questions

---

## Version Control

### Versioning Scheme
- **Development:** v0.x.x (not production-ready)
- **Beta:** v0.9.x (feature-complete, testing)
- **Production:** v1.x.x (stable, client-facing)
- **Major updates:** v2.x.x (breaking changes)

### Tagging Releases
```bash
# In Git
git tag -a v1.0.0 -m "Initial production release"
git push origin v1.0.0
```

**In Anvil:**
- Publish app
- Note version in description
- Update changelog

---

## Security Considerations

### Anvil Account Security
- **Strong passwords** (16+ characters, unique)
- **Two-factor authentication** enabled
- **Limited access** (only authorized MyBizz staff)
- **Separate accounts** for staging vs production

### Client Instance Security
- **MyBizz retains Anvil credentials** (for support)
- **Client receives app admin credentials** (different from Anvil)
- **Secrets properly configured** (never hardcoded)
- **HTTPS enforced** (Anvil default)

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-31 | Dev Team | Initial Anvil setup procedure |

---

**Last Updated:** December 31, 2025  
**Next Review:** After first client instance setup (real-world experience)
