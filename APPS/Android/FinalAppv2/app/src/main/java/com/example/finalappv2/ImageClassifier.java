package com.example.finalappv2;

import android.app.Activity;
import android.content.res.AssetFileDescriptor;
import android.graphics.Bitmap;
import android.util.Log;

import org.tensorflow.lite.Interpreter;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.FileChannel;

public abstract class ImageClassifier {

    private ByteBuffer tfliteModel;
    protected Interpreter tflite;
    protected ByteBuffer imgData;
    private static final int DIM_BATCH_SIZE = 1;
    private static final int DIM_PIXEL_SIZE = 3;
    private int[] intValues = new int[getImageSizeX() * getImageSizeY()];
    private final Interpreter.Options tfliteOptions = new Interpreter.Options();

    ImageClassifier(Activity activity) throws IOException {
        tfliteModel = loadModelFile(activity);
        Log.i("INFO", "loaded model...");
        tflite = new Interpreter(tfliteModel, tfliteOptions);
        imgData =
                ByteBuffer.allocateDirect(
                        DIM_BATCH_SIZE
                                *getImageSizeX()
                                *getImageSizeY()
                                *DIM_PIXEL_SIZE
                                *getNumBytesPerChannel());
        imgData.order(ByteOrder.nativeOrder());
        Log.i("INFO", "Created a Tensorflow Lite Image Classifier!");

    }

    private ByteBuffer loadModelFile(Activity activity) throws IOException {
        AssetFileDescriptor fileDescriptor = activity.getAssets().openFd(getModelPath());
        FileInputStream inputStream = new FileInputStream(fileDescriptor.getFileDescriptor());
        FileChannel fileChannel = inputStream.getChannel();
        long startOffset = fileDescriptor.getStartOffset();
        long declaredLength = fileDescriptor.getDeclaredLength();
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
    }

    private void convertBitmapToByteBuffer(Bitmap bitmap) {
        if(imgData == null){
            return;
        }
        imgData.rewind();
        bitmap.getPixels(intValues, 0, bitmap.getWidth(), 0, 0, bitmap.getWidth() ,bitmap.getHeight());
        int pixel = 0;
        for (int i = 0; i < getImageSizeX(); ++i) {
            for (int j = 0; j < getImageSizeY(); ++j) {
                final int val = intValues[pixel++];
                addPixelValue(val);
            }
        }
    }

    void classifyFrame(Bitmap bitmap){
        if (tflite == null){
            Log.e("ERR", "Image classifier has not been initialized; Skipped.");
            return;
        }
        convertBitmapToByteBuffer(bitmap);
        runInference();
    }

    private void recreateInterpreter() {
        if (tflite != null){
            tflite.close();
            tflite = new Interpreter(tfliteModel, tfliteOptions);
        }
    }

    public void setNumThreads(int numThreads){
        tfliteOptions.setNumThreads(numThreads);
        recreateInterpreter();
    }

    public void close(){
        tflite.close();
        tflite = null;
        tfliteModel = null;
    }

    protected abstract String getModelPath();
    protected abstract int getImageSizeX();
    protected abstract int getImageSizeY();
    protected abstract int getNumBytesPerChannel();
    protected abstract void addPixelValue(int pixelValue);
    protected abstract void runInference();
    protected abstract float[][] getBoxes();
    protected abstract float[] getScores();
    protected abstract float[] getClasses();
}
