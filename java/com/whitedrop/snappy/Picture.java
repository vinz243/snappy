package com.whitedrop.snappy;

/**
 * Created by vinz243 on 16/06/16.
 */
public class Picture {
    private String path, mime;
    private int id;

    public int getId() {
        return id;
    }

    public String getPath() {
        return path;
    }

    public String getMime() {
        return mime;
    }

    public void setId(int id) {
        this.id = id;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public void setMime(String mime) {
        this.mime = mime;
    }

    public String toString() {
        return path;
    }

    public static class PictureBuilder {
        private Picture mPicture;
        public PictureBuilder() {
            mPicture = new Picture();
        }

        public PictureBuilder id(int id) {
            mPicture.setId(id);
            return this;
        }
        public PictureBuilder path(String path){
            mPicture.setPath(path);
            return this;
        }
        public PictureBuilder mime(String mime) {
            mPicture.setMime(mime);
            return this;
        }
        public Picture build() {
            return mPicture;
        }

    }
}
