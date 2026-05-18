package com.premkr.pixeltetris;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.webkit.MimeTypeMap;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.io.IOException;
import java.io.InputStream;

public class MainActivity extends Activity {
    private static final String APP_HOST = "pixel-tetris.local";
    private static final String START_URL = "https://" + APP_HOST + "/index.html";

    @Override
    @SuppressLint("SetJavaScriptEnabled")
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        WebView webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(17, 19, 22));
        webView.setWebViewClient(new LocalAssetClient());

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);

        getWindow().setStatusBarColor(Color.rgb(17, 19, 22));
        getWindow().setNavigationBarColor(Color.rgb(17, 19, 22));
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
        );

        setContentView(webView);
        webView.loadUrl(START_URL);
    }

    private final class LocalAssetClient extends WebViewClient {
        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
            Uri uri = request.getUrl();
            if (!"https".equals(uri.getScheme()) || !APP_HOST.equals(uri.getHost())) {
                return null;
            }

            String path = uri.getPath();
            if (path == null || "/".equals(path)) {
                path = "/index.html";
            }

            String assetPath = "www" + path;
            try {
                InputStream stream = getAssets().open(assetPath);
                return new WebResourceResponse(mimeType(assetPath), "UTF-8", stream);
            } catch (IOException ignored) {
                return new WebResourceResponse("text/plain", "UTF-8", null);
            }
        }
    }

    private static String mimeType(String path) {
        if (path.endsWith(".webmanifest")) {
            return "application/manifest+json";
        }

        String extension = MimeTypeMap.getFileExtensionFromUrl(path);
        String type = MimeTypeMap.getSingleton().getMimeTypeFromExtension(extension);
        if (type != null) {
            return type;
        }

        if (path.endsWith(".js")) return "text/javascript";
        if (path.endsWith(".css")) return "text/css";
        if (path.endsWith(".svg")) return "image/svg+xml";
        return "application/octet-stream";
    }
}
