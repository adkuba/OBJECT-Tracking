package com.example.finalappv2;

import android.app.Activity;

import java.io.IOException;
import java.util.Map;
import java.util.TreeMap;

public class ImageClassifierQuantizedMobileNet extends ImageClassifier {
    private float[][][] boxes = new float[1][10][4];
    private float[][] scores = new float[1][10];
    private float[][] classes = new float[1][10];
    private Map<Integer, Object> output_map = new TreeMap<>();
    private Object[] input_data = new Object[1];;

    ImageClassifierQuantizedMobileNet(Activity activity) throws IOException {
        super(activity);
        output_map.put(0, boxes);
        output_map.put(1, classes);
        output_map.put(2, scores);
    }
    @Override
    protected String getModelPath(){
        return "q_detect.tflite";
    } //mobilenetv2_ssd_quantized_coco

    @Override
    protected int getImageSizeX() {
        return 300;
    }

    @Override
    protected int getImageSizeY() {
        return 300;
    }

    @Override
    protected int getNumBytesPerChannel() {
        return 1;
    }

    @Override
    protected void addPixelValue(int pixelValue) {
        imgData.put((byte) ((pixelValue >> 16) & 0xFF));
        imgData.put((byte) ((pixelValue >> 8) & 0xFF));
        imgData.put((byte) (pixelValue & 0xFF));
    }

    @Override
    protected void runInference() {
        input_data[0] = imgData;
        tflite.runForMultipleInputsOutputs(input_data, output_map);
    }

    @Override
    protected float[][] getBoxes(){
        return boxes[0];
    }

    @Override
    protected float[] getScores(){
        return scores[0];
    }

    @Override
    protected float[] getClasses(){
        return classes[0];
    }
}