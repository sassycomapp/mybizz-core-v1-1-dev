# MyBizz Platform - Required Edits Log

**Created:** January 2, 2026  
**Purpose:** Track all document edits identified during development planning refinement  
**Status:** Living Document

# IMPORTANT!
This  document was constructed before and during the current revision of the 01_conceptual_plan.md document. Some of these proposed edits may now already be redundant or requiring to be changed, etc.
Be governed by the 01_conceptual_plan.md  document.

---

## Priority 1: Critical Inconsistencies

### 1.1 **00_docs_map.md** - Remove Real Estate Verticals
**Lines:** ~250-270, 75-84, multiple other references  
**Issue:** Document still references "re_sales" and "re_rentals" verticals which have been dropped  
**Action Required:** 
- Remove all references to Real Estate verticals (re_sales, re_rentals)
- Update vertical count from "10 verticals" to "4 verticals"
- Update app-specific documentation sections for dropped verticals
- Update total documentation count (currently shows ~186 docs, many are for dropped verticals)

**Lines to update:**
- Line 75-84: Vertical types list in database schema
- Lines ~250-270: App-specific documentation for Real Estate apps
- Any references to "10 verticals supported" → "4 verticals supported"

---

### 1.2 **01_conceptual_design.md** - Complete Rewrite Required
**Current Status:** ✅ COMPLETE (Version 4.0 with Open Verticals)  
**Issue:** Document was grossly deficient, did not properly describe the project  
**Action Taken:** Complete rewrite including:
- ✅ Open Verticals architecture (all features available to all clients)
- ✅ Modular page component system for website templates
- ✅ Permission-based user role system (Owner/Manager/Admin/Staff/Customer/Visitor)
- ✅ Navigation structure marked as "Pending further conceptual design"
- ✅ Simplified theme customization (write to properties)
- ✅ Multi-currency system aligned with Stripe/PayPal requirements
- ✅ Frontend content editing system (component-based image/text updates)
- ✅ Social media integrations (Facebook, Instagram, X, LinkedIn, WhatsApp share button)
- ✅ Transaction-type-based metadata validation
- ✅ Backup destinations (Email + AWS S3 with client setup guide)
- ✅ Comprehensive founding statement describing entire MyBizz vision

**Date Completed:** January 2, 2026

---

### 1.3 **06_database-schema.md** - Update Vertical Types
**Lines:** 73-84  
**Issue:** Lists 10 vertical types including dropped Real Estate verticals  
**Action Required:**
- Remove `re_sales` from vertical types
- Remove `re_rentals` from vertical types
- Update to show only 4 verticals:
  - hospitality
  - consulting (encompasses: consulting, online_services, physical_services)
  - e-commerce (encompasses: digital_products, physical_products)
  - memberships

---

### 1.4 **Multiple Documents** - Update Subscriber Target
**Documents:** All planning documents  
**Issue:** Some documents still reference "1,000 subscribers" target  
**Action Required:** Global search and replace of "1,000 subscribers" → "250 subscribers"

**Known locations:**
- 01_conceptual_design.md (already updated to 250)
- 03_dev_plan.md (already updated to 250)
- 04_architecture_specification.md (already updated to 250)
- Check other documents for any remaining "1,000" references

---

## Priority 2: Alignment Issues

### 2.1 **03_dev_plan.md** - Vertical Count References
**Multiple locations**  
**Issue:** Some narrative text may still refer to "10 verticals"  
**Action Required:** Review and update all references to "4 verticals"; Update entire file to represent 01_conceptual_design & 04_architecture_specification.md

---

### 2.2 **10_MyBizz_Gantt_Chart.xlsx** - Obsolete
**Status:** User has confirmed this document is now obsolete  
**Action Required:** 
- Create new document: `10_project_log.md` to replace Gantt chart
- Update 00_docs_map.md to reflect this change
- Update ops_gantt_management.md or create new ops_project_log_management.md

---

## Priority 3: Documentation Completeness

### 3.1 **ops_project_log_management.md** - New Document Needed
**Status:** Doesn't exist yet  
**Issue:** Gantt chart is being replaced with Project Log, need procedures for managing it  
**Action Required:** Create operational procedure document for Project Log management

---

### 3.2 **10_project_log.md** - New Document Needed
**Status:** Doesn't exist yet  
**Issue:** Replacement for Gantt chart  
**Action Required:** Create perpetual project log document that:
- Follows on from 03_dev_plan.md
- Records daily tasks accomplished
- Tracks what's done, in progress, on hold
- Replaces Gantt chart with simpler continuous living doc

---

## Priority 4: Cascading Changes from Strategic Decisions

### 4.1 Update App-Specific Documentation References
**Issue:** With Real Estate verticals dropped, many app-specific docs in 00_docs_map.md are no longer needed  
**Action Required:**
- Review app_re_sales_* documentation references
- Review app_re_rentals_* documentation references
- Mark as ❌ Not Applicable or remove entirely
- Update total documentation count

---

### 4.2 **08_sitemap.md** - Review Route Count
**Issue:** Sitemap shows 181+ routes, may include routes for dropped verticals  
**Action Required:** Review sitemap and remove any Real Estate specific routes

---

## Change Log

| Date | Editor | Changes Made |
|------|--------|--------------|
| 2026-01-02 | Claude (AI) | Initial Required Edits log created during conceptual design rewrite |

---

## Notes

**How to Use This Log:**
- Add new edits as they're identified during work
- Mark edits as complete with ✅ when done
- Keep Priority 1 issues at top
- Update change log when making edits
- Reference this document in conversations with AI and human

**Edit Priority Levels:**
- **Priority 1: Critical Inconsistencies** - Factual errors, outdated info
- **Priority 2: Alignment Issues** - Docs don't match each other
- **Priority 3: Documentation Completeness** - Missing docs or procedures
- **Priority 4: Cascading Changes** - Updates needed due to strategic decisions

---

**Last Updated:** January 2, 2026  
**Total Edits Identified:** 11  
**Total Edits Completed:** 1 (01_conceptual_design.md v4.0)  
**In Progress:** 0  
**Remaining:** 10 (00_docs_map, 06_database-schema, multiple docs for subscriber count, verticals, project log creation)


--------------------------------------------------
# NEW Work:
##05_nomenclature

Order as follows:
MyBizz V1.x - This current initial version.
MyBizz V2.x - The next iteration of the MyBizz Platform (some things have been planned in some documents)
App: define this and the naming convention
Phase: define this and the naming convention
stage: define this and the naming convention
Task: define this and the naming convention

##03_dev_plan
###Strategic planning:
- Broad Scaffold:
  - Apply: "Docs\anvil_packages_namespaces.md" to create the skeleton scaffold. Do not attempt to scaffold the entire MyBizz Project. Rather design the scaffold schema with 2 tiers (the 3rd tier will be created during development).
  - All forms and modules to be created must be identified according to placement.
  - The Anvil Assets storage facility exists as a path, this may need some scaffolding to facilitate the app.
