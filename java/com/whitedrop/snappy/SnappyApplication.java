package com.whitedrop.snappy;

import android.app.Application;
import android.util.Log;

import com.facebook.drawee.backends.pipeline.Fresco;

/**
 * Created by vinz243 on 17/06/16.
 */
public class SnappyApplication extends Application{
    @Override
    public void onCreate() {
        super.onCreate();
        Fresco.initialize(this);
    }
}
