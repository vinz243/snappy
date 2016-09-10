package com.whitedrop.snappy;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.PermissionChecker;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.ContentFrameLayout;
import android.support.v7.widget.RecyclerView;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.util.TypedValue;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.widget.ImageView;
import android.widget.TextView;

import com.facebook.drawee.backends.pipeline.Fresco;
import com.facebook.drawee.view.SimpleDraweeView;
import com.fivehundredpx.greedolayout.GreedoLayoutManager;
import com.fivehundredpx.greedolayout.GreedoLayoutSizeCalculator;
import com.fivehundredpx.greedolayout.GreedoSpacingItemDecoration;

import java.io.File;
import java.util.ArrayList;


public class MainActivity extends AppCompatActivity implements ActivityCompat.OnRequestPermissionsResultCallback{

    public final int PERMISSION_REQUEST_READ_EXTERNAL_STORAGE = 0x42;

    public static final String TAG = "MainActivity";
    private View mView;
    private Context mContext;
    private PictureProvider mPictureProvider;
    private ArrayList<Picture> mPictures;


    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions,
                                           int[] grantResults) {
        if (requestCode == PERMISSION_REQUEST_READ_EXTERNAL_STORAGE) {
            // BEGIN_INCLUDE(permission_result)
            // Received permission result for camera permission.
            Log.i(TAG, "Received response for storage permission request.");

            // Check if the only required permission has been granted
            if (grantResults.length == 1 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                // Camera permission has been granted, preview can be displayed
                Log.i(TAG, "STORAGE permission has now been granted. Showing preview.");
                Snackbar.make(mView, R.string.storage_perm_allowed,
                        Snackbar.LENGTH_SHORT).show();
            } else {
                Log.i(TAG, "STORAGE permission was NOT granted.");
                Snackbar.make(mView, R.string.storage_perm_denied,
                        Snackbar.LENGTH_SHORT).show();

            }
            // END_INCLUDE(permission_result)

        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mContext = this.getApplicationContext();
        mPictureProvider = new PictureProvider(this);
        mPictures = mPictureProvider.getPicturesList();

        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        mView = findViewById(R.id.coordinator_layout);

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(mView, "Requesting storage", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
                requestStoragePermission();
            }
        });

        PictureRecyclerAdapter recyclerAdapter = new PictureRecyclerAdapter();
        GreedoLayoutManager layoutManager = new GreedoLayoutManager(recyclerAdapter);

        layoutManager.setMaxRowHeight(200);

        RecyclerView recyclerView = (RecyclerView)findViewById(R.id.recycler_view);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.ECLAIR_MR1) {
            recyclerView.addItemDecoration(
                    new GreedoSpacingItemDecoration(
                            (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 4,
                                    mContext.getResources().getDisplayMetrics())));
            recyclerView.setLayoutManager(layoutManager);
            recyclerView.setAdapter(recyclerAdapter);
        }

// Set the max row height in pixels
        layoutManager.setMaxRowHeight(300);


        Window window = this.getWindow();
        window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        window.clearFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS);


        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            window.setStatusBarColor(this.getResources().getColor(R.color.colorPrimaryDark));
        }


    }
    @Override
    protected void onStart() {
        super.onStart();
        requestStoragePermission();
    }
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }
    private void requestStoragePermission() {
        // Here, thisActivity is the current activity
        if (/*ContextCompat.checkSelfPermission(this,
                Manifest.permission.READ_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED*/
                PermissionChecker.checkSelfPermission(this,
                        Manifest.permission.READ_EXTERNAL_STORAGE)
                        != PermissionChecker.PERMISSION_GRANTED) {

            // Should we show an explanation?
            if (ActivityCompat.shouldShowRequestPermissionRationale(this,
                    Manifest.permission.READ_EXTERNAL_STORAGE)) {
                final Activity self = this;
                Snackbar.make(mView, R.string.storage_perm_rationale,
                        Snackbar.LENGTH_LONG).setAction(R.string.allow_storage, new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {

                        ActivityCompat.requestPermissions(self,
                                new String[]{Manifest.permission.READ_EXTERNAL_STORAGE},
                                PERMISSION_REQUEST_READ_EXTERNAL_STORAGE);
                    }
                });
                // Show an expanation to the user *asynchronously* -- don't block
                // this thread waiting for the user's response! After the user
                // sees the explanation, try again to request the permission.

            } else {

                // No explanation needed, we can request the permission.

                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.READ_EXTERNAL_STORAGE},
                        PERMISSION_REQUEST_READ_EXTERNAL_STORAGE);

                // MY_PERMISSIONS_REQUEST_READ_CONTACTS is an
                // app-defined int constant. The callback method gets the
                // result of the request.
            }
        } else {
            Snackbar.make(mView, "Storage enabled", Snackbar.LENGTH_LONG)
                    .setAction("Action", null).show();

        }
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }
    protected static class PictureViewHolder extends RecyclerView.ViewHolder {

        private ImageView mImageView;

        public PictureViewHolder(ImageView imageView) {
            super(imageView);
            mImageView = imageView;
        }
    }
    protected class PictureRecyclerAdapter extends RecyclerView.Adapter<PictureViewHolder> implements GreedoLayoutSizeCalculator.SizeCalculatorDelegate {

        @Override
        public PictureViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
            SimpleDraweeView draweeView = new SimpleDraweeView(mContext);
            draweeView.setScaleType(SimpleDraweeView.ScaleType.CENTER_CROP);
            draweeView.setBackgroundResource(R.color.colorPrimary);

            draweeView.setLayoutParams(new ViewGroup.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.MATCH_PARENT
            ));
            return new PictureViewHolder(draweeView);

        }

        @Override
        public void onBindViewHolder(PictureViewHolder holder, int position) {
            Log.d(TAG, "onbind " + String.valueOf(mPictures.get(position)));
            holder.mImageView.setImageURI(Uri.parse("file://" + String.valueOf(mPictures.get(position))));
        }

        @Override
        public int getItemCount() {
            return mPictures.size();
        }

        @Override
        public double aspectRatioForIndex(int i) {
            if (this.getItemCount() <= i) {
              Log.e(TAG, "We've got past the end of list? wtf");
              Log.d(TAG, "Just to remind, we have " + this.getItemCount() + " items");
              return 1;
            }

            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inJustDecodeBounds = true;

            Log.d(TAG, mPictures.get(i).getPath());

            BitmapFactory.decodeFile(mPictures.get(i).getPath(), options);
            return options.outWidth / (double) options.outHeight;
        }
    }
}
