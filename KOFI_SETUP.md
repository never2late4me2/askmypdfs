# Ko-fi Monetization Setup Guide

## ✅ Ko-fi Integration Added

Your app now includes Ko-fi donation buttons in two versions:

### Version 1: Footer Ko-fi Button (`app.py`)
- Ko-fi button appears at the bottom of the page
- Centered and prominent
- Best for single-page focus

### Version 2: Sidebar Ko-fi Widget (`app_with_sidebar_kofi.py`)
- Ko-fi button in the sidebar
- Always visible while scrolling
- Includes "How to Use" and "Tech Stack" info
- Better for persistent visibility

## 🔗 Your Ko-fi Link

The apps are currently configured with:
```
https://ko-fi.com/bryantolbert
```

### To Update Your Ko-fi Username:

**If your Ko-fi username is different**, update these lines:

**In `app.py` (line 204):**
```html
<a href='https://ko-fi.com/YOUR_USERNAME' target='_blank'>
```

**In `app_with_sidebar_kofi.py` (line 38):**
```html
<a href='https://ko-fi.com/YOUR_USERNAME' target='_blank'>
```

Replace `YOUR_USERNAME` with your actual Ko-fi username.

## 🎨 Ko-fi Button Features

The integration includes:
- ✅ Official Ko-fi button image
- ✅ Opens in new tab (doesn't interrupt app usage)
- ✅ Responsive design
- ✅ Professional styling
- ✅ Works on all devices

## 📊 Tracking Donations

To track donations:
1. Log into your Ko-fi account at https://ko-fi.com
2. Go to your Dashboard
3. View "Supporters" and "Donations" sections
4. Ko-fi provides analytics on:
   - Number of supporters
   - Total donations
   - Recent activity

## 💰 Ko-fi Payment Options

Your supporters can donate via:
- Credit/Debit cards
- PayPal
- Apple Pay
- Google Pay

Ko-fi takes a small platform fee (0% on one-time donations with Ko-fi Gold).

## 🚀 Testing the Ko-fi Button

### Local Testing:
1. Run the app: `streamlit run app.py`
2. Scroll to the bottom (or check sidebar in alternative version)
3. Click the Ko-fi button
4. Verify it opens your Ko-fi page in a new tab

### Production Testing:
1. Deploy to Streamlit Cloud
2. Visit your live app URL
3. Click the Ko-fi button
4. Confirm it redirects correctly

## 🎯 Best Practices for Monetization

1. **Add a compelling message**: Consider adding text like:
   - "Enjoying this tool? Support development!"
   - "Buy me a coffee to keep this free!"
   
2. **Show value first**: Let users try the app before seeing donation requests

3. **Be transparent**: Mention what donations support (server costs, development time, etc.)

4. **Multiple placements**: Consider both footer and sidebar for maximum visibility

5. **Track conversions**: Monitor Ko-fi analytics to see what works

## 📝 Customization Options

### Change Button Text:
Add custom text above the button:
```python
st.markdown("### ☕ Enjoying this app? Buy me a coffee!")
```

### Add Custom Styling:
Modify the button appearance:
```html
<div style='text-align:center; padding: 20px; background-color: #f0f0f0; border-radius: 10px;'>
    <a href='https://ko-fi.com/bryantolbert' target='_blank'>
        <img height='40' src='https://storage.ko-fi.com/cdn/kofi2.png?v=3' />
    </a>
</div>
```

### Add Goal Widget:
Ko-fi offers embeddable goal widgets. Get the code from your Ko-fi dashboard.

## ⚠️ Important Notes

- **Ko-fi account required**: Make sure you have an active Ko-fi account
- **Username must match**: The link must point to your actual Ko-fi profile
- **Test before deploying**: Always verify the link works correctly
- **Streamlit Cloud**: Ko-fi buttons work perfectly on Streamlit Cloud (no special config needed)

## 🔧 Troubleshooting

**Button doesn't appear:**
- Check that `unsafe_allow_html=True` is set
- Verify the HTML is properly formatted

**Link doesn't work:**
- Confirm your Ko-fi username is correct
- Test the link directly in a browser
- Ensure your Ko-fi page is public

**Button looks wrong:**
- Clear browser cache
- Check Ko-fi CDN is accessible
- Try the alternative button URL: `https://ko-fi.com/img/githubbutton_sm.svg`

## 📞 Support

If you need help with Ko-fi:
- Ko-fi Help Center: https://help.ko-fi.com
- Ko-fi Support: support@ko-fi.com

For app-related issues, check the main README.md file.
