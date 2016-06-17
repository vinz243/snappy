package com.whitedrop.snappy;

import android.app.Activity;
import android.content.ContentResolver;
import android.database.Cursor;
import android.provider.MediaStore;
import android.provider.MediaStore.Images.ImageColumns;
import java.util.ArrayList;

public class PictureProvider  {

    public interface PictureReceiver {
        void onReceivePictures(ArrayList<Picture> paths);
    }
    private Activity activity;
    private ArrayList<Picture> picturesListCache = new ArrayList<Picture>();
    private boolean listCached = false;

    public PictureProvider(Activity activity) {
        this.activity = activity;
    }


    public ArrayList<Picture> getPicturesList() {
        return getPicturesList(false);
    }

    public ArrayList<Picture> getPicturesList(boolean clearCache) {

        if(!clearCache && listCached) return picturesListCache;

        picturesListCache.clear();
        picturesListCache.addAll(getAllPictures(this.activity));
        listCached = true;
        return (ArrayList<Picture>) picturesListCache.clone();
    }


    private static ArrayList<Picture> getAllPictures(Activity activity) {
        ContentResolver cr = activity.getApplicationContext().getContentResolver();

        String[] columns = new String[] {
                ImageColumns._ID,
                ImageColumns.TITLE,
                ImageColumns.DATA,
                ImageColumns.MIME_TYPE,
                ImageColumns.SIZE};
        Cursor cur = cr.query(MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                columns, null, null, null);
        ArrayList<Picture> pics = new ArrayList<Picture>();
        while (cur.moveToNext()) {
            Picture pic = new Picture.PictureBuilder()
                    .id(cur.getInt(0))
                    .path(cur.getString(2))
                    .mime(cur.getString(3))
                    .build();
            pics.add(pic);

        }
        return pics;
    }


}
