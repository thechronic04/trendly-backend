# Vercel Speed Insights for FastAPI Backend

This document explains how Vercel Speed Insights has been integrated into the Trendly Backend API.

## What is Speed Insights?

Vercel Speed Insights measures Core Web Vitals and other performance metrics from real users visiting your application. While Speed Insights is primarily designed for frontend applications, this integration adds tracking to the FastAPI backend's HTML responses, particularly the auto-generated API documentation pages (Swagger UI and ReDoc).

## Implementation Details

### Files Modified

1. **`app/core/speed_insights.py`** (NEW)
   - Custom middleware that injects Speed Insights script into HTML responses
   - Setup function for easy integration with FastAPI apps
   - Automatically adds tracking to Swagger UI and ReDoc documentation pages

2. **`app/main.py`**
   - Imported and initialized Speed Insights middleware
   - Automatically applies to all HTML responses from the application

3. **`api/index.py`**
   - Added Speed Insights middleware inline
   - Tracks the Vercel-hosted API endpoint

4. **`main.py`**
   - Added Speed Insights middleware inline
   - Tracks the standalone API endpoint

### How It Works

The implementation uses a FastAPI/Starlette middleware that:

1. Intercepts all HTTP responses
2. Checks if the response is HTML (status 200 with `text/html` content type)
3. Injects the Speed Insights tracking script before the closing `</body>` or `</html>` tag
4. Returns the modified HTML response

The injected script follows Vercel's official implementation:

```html
<script>
  window.si = window.si || function () { (window.siq = window.siq || []).push(arguments); };
</script>
<script defer src="/_vercel/speed-insights/script.js"></script>
```

## Enabling Speed Insights on Vercel

To complete the setup and start collecting metrics, follow these steps:

### 1. Enable Speed Insights in Your Vercel Dashboard

1. Go to your [Vercel Dashboard](https://vercel.com/dashboard)
2. Select the **trendly-backend** project
3. Navigate to the **Speed Insights** tab
4. Click **Enable**

> **Note:** Enabling Speed Insights will add new routes scoped at `/_vercel/speed-insights/*` after your next deployment.

### 2. Deploy Your Application

Deploy your FastAPI application to Vercel:

```bash
vercel deploy
```

Or connect your Git repository to enable automatic deployments on every push.

### 3. Verify the Integration

After deployment, check that Speed Insights is working:

1. Visit your API documentation pages:
   - Main docs: `https://your-app.vercel.app/api/v1/docs`
   - ReDoc: `https://your-app.vercel.app/api/v1/redoc`

2. Open your browser's developer tools (F12)

3. Check the Network tab for requests to `/_vercel/speed-insights/script.js`

4. Check the HTML source and verify the Speed Insights scripts are present before `</body>`

### 4. View Your Data

Once users visit your API documentation:

1. Go to your [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Click the **Speed Insights** tab
4. View real-time performance metrics

> **Note:** It may take a few hours to a few days for meaningful data to accumulate.

## What Gets Tracked

Speed Insights tracks the following for HTML pages:

- **Core Web Vitals:**
  - LCP (Largest Contentful Paint)
  - FID (First Input Delay)
  - CLS (Cumulative Layout Shift)
  - TTFB (Time to First Byte)

- **Other Metrics:**
  - FCP (First Contentful Paint)
  - INP (Interaction to Next Paint)

## Use Cases for Backend APIs

While Speed Insights is primarily for frontend apps, it's useful for FastAPI backends in these scenarios:

1. **API Documentation Performance:** Track how fast Swagger UI and ReDoc load for developers
2. **Admin Panels:** If you add HTML admin interfaces to your API
3. **Server-Rendered Pages:** Any HTML content served by the API
4. **Marketing/Landing Pages:** If the API serves any static HTML pages

## Configuration

The Speed Insights integration is enabled by default. To disable it:

### In `app/main.py`:

```python
# Comment out or remove this line:
setup_speed_insights(app)
```

### In `api/index.py` and `main.py`:

```python
# Comment out or remove this line:
app.add_middleware(SpeedInsightsMiddleware)
```

## Privacy and Compliance

Speed Insights is designed with privacy in mind:

- No personal data is collected
- All data is anonymous and aggregated
- Compliant with GDPR and other privacy regulations

Learn more: [Speed Insights Privacy Policy](https://vercel.com/docs/speed-insights/privacy-policy)

## Additional Resources

- [Vercel Speed Insights Documentation](https://vercel.com/docs/speed-insights)
- [Speed Insights Metrics](https://vercel.com/docs/speed-insights/metrics)
- [Speed Insights Limits and Pricing](https://vercel.com/docs/speed-insights/limits-and-pricing)
- [Troubleshooting Guide](https://vercel.com/docs/speed-insights/troubleshooting)

## Next Steps

1. Deploy your application to Vercel
2. Enable Speed Insights in the dashboard
3. Wait for traffic to accumulate
4. Analyze performance metrics
5. Optimize based on insights

For questions or issues, refer to the Vercel documentation or contact Vercel support.
