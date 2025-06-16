# 💤 Put Orpheus-3b Deployment to Sleep

## **Deployment ID**: `yqv0epjw` (Orpheus-3b)

### **Steps to Put Deployment to Sleep:**

1. **Go to Baseten Dashboard**: https://www.baseten.co/dashboard

2. **Find Your Deployment**:
   - Look for deployment with ID: `yqv0epjw`
   - Should be labeled as "Orpheus-3b" or similar

3. **Access Deployment Settings**:
   - Click on the deployment name/card
   - Navigate to deployment details page

4. **Put to Sleep**:
   - Look for "Sleep", "Pause", or "Stop" button
   - Click to put the deployment to sleep
   - Confirm the action when prompted

### **What This Does**:
- ✅ **Stops billing** for the deployment
- ✅ **Preserves configuration** for future use
- ✅ **Keeps deployment definition** intact
- ❌ **Stops serving requests** until reactivated

### **To Reactivate Later**:
- Return to the same deployment
- Click "Wake" or "Resume" button
- Deployment will restart (may take a few minutes)

### **Alternative: CLI Method**
If you have Baseten CLI installed:
```bash
baseten deployment pause yqv0epjw
```

### **Confirmation**
Once sleeping, the deployment status should show:
- Status: "Sleeping" or "Paused"
- Billing: Stopped
- Requests: Will return 503 errors

**💡 This will save costs while keeping the deployment ready for future use!** 