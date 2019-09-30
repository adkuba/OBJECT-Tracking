package com.example.finalappv2;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.PixelFormat;
import android.graphics.Point;
import android.graphics.PorterDuff;
import android.graphics.RectF;
import android.graphics.SurfaceTexture;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraCaptureSession;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraDevice;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.CameraMetadata;
import android.hardware.camera2.CaptureRequest;
import android.hardware.camera2.params.StreamConfigurationMap;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.SystemClock;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.util.Size;
import android.util.SparseIntArray;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.Surface;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.TextureView;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.RelativeLayout;
import android.widget.Toast;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;

public class Camera2BasicFragment extends Fragment implements ActivityCompat.OnRequestPermissionsResultCallback, View.OnClickListener {

    private static final int CAMERA_REQUEST_CODE = 1;
    private final Object lock = new Object();
    private CameraDevice cameraDevice;
    private Handler backgroundHandler;
    private ImageClassifier classifier;
    private AutoFitTextureView textureView;
    private CameraManager cameraManager;
    private Size previewSize;
    private String cameraId;
    private HandlerThread backgroundThread;
    private CaptureRequest.Builder captureRequestBuilder;
    private CaptureRequest captureRequest;
    private CameraCaptureSession cameraCaptureSession;
    private boolean runClassifier = false;
    private Semaphore CameraOpenCloseLock = new Semaphore(1);
    private Size mVideoSize;
    private MediaRecorder mMediaRecorder;
    private String mNextVideoAbsolutePath;
    private Integer mSensorOrientation;
    private static final int SENSOR_ORIENTATION_DEFAULT_DEGREES = 90;
    private static final int SENSOR_ORIENTATION_INVERSE_DEGREES = 270;
    private static final SparseIntArray DEFAULT_ORIENTATIONS = new SparseIntArray();
    private static final SparseIntArray INVERSE_ORIENTATIONS = new SparseIntArray();
    private Button mButtonVideo;
    private Button resetButton;
    private boolean mIsRecordingVideo;
    private SurfaceView surfaceView;
    private SurfaceHolder surfaceHolder;
    private Point clicked = new Point(-1, -1);
    private Bitmap last;
    private ImageView lastview;
    private float lastid;

    static {
        DEFAULT_ORIENTATIONS.append(Surface.ROTATION_0, 90);
        DEFAULT_ORIENTATIONS.append(Surface.ROTATION_90, 0);
        DEFAULT_ORIENTATIONS.append(Surface.ROTATION_180, 270);
        DEFAULT_ORIENTATIONS.append(Surface.ROTATION_270, 180);
    }

    static {
        INVERSE_ORIENTATIONS.append(Surface.ROTATION_0, 270);
        INVERSE_ORIENTATIONS.append(Surface.ROTATION_90, 180);
        INVERSE_ORIENTATIONS.append(Surface.ROTATION_180, 90);
        INVERSE_ORIENTATIONS.append(Surface.ROTATION_270, 0);
    }

    private static final String[] VIDEO_PERMISSIONS = {
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
    };

    private final TextureView.SurfaceTextureListener surfaceTextureListener = new TextureView.SurfaceTextureListener(){
        @Override
        public void onSurfaceTextureAvailable(SurfaceTexture surfaceTexture, int width, int height){
            openCamera(width, height);
        }
        @Override
        public void onSurfaceTextureSizeChanged(SurfaceTexture surfaceTexture, int width, int height){
            configureTransform(width, height);
        }
        @Override
        public boolean onSurfaceTextureDestroyed(SurfaceTexture surfaceTexture) {
            return true;
        }
        @Override
        public void onSurfaceTextureUpdated(SurfaceTexture surfaceTexture){ }
    };

    private final CameraDevice.StateCallback stateCallback = new CameraDevice.StateCallback() {
        @Override
        public void onOpened(@NonNull CameraDevice currentCameraDevice) {
            cameraDevice = currentCameraDevice;
            createPreviewSession();
            CameraOpenCloseLock.release();
            if (null != textureView) {
                configureTransform(textureView.getWidth(), textureView.getHeight());
            }
        }

        @Override
        public void onDisconnected(@NonNull CameraDevice currentCameraDevice) {
            CameraOpenCloseLock.release();
            currentCameraDevice.close();
            cameraDevice = null;
        }

        @Override
        public void onError(@NonNull CameraDevice currentCameraDevice, int error) {
            CameraOpenCloseLock.release();
            currentCameraDevice.close();
            cameraDevice = null;
            Activity activity = getActivity();
            if (activity != null) {
                activity.finish();
            }
        }
    };

    private static Size chooseVideoSize(Size[] choices) {
        for (Size size : choices) {
            if (size.getWidth() == size.getHeight() * 4 / 3 && size.getWidth() <= 1080) {
                return size;
            }
        }
        Log.e("ERR", "Couldn't find any suitable video size");
        return choices[choices.length - 1];
    }

    private static Size chooseOptimalSize(Size[] choices, int width, int height, Size aspectRatio) {
        // Collect the supported resolutions that are at least as big as the preview Surface
        List<Size> bigEnough = new ArrayList<>();
        int w = aspectRatio.getWidth();
        int h = aspectRatio.getHeight();
        for (Size option : choices) {
            if (option.getHeight() == option.getWidth() * h / w &&
                    option.getWidth() >= width && option.getHeight() >= height) {
                bigEnough.add(option);
            }
        }

        // Pick the smallest of those, assuming we found any
        if (bigEnough.size() > 0) {
            return Collections.min(bigEnough, new CompareSizesByArea());
        } else {
            Log.e("ERR", "Couldn't find any suitable preview size");
            return choices[0];
        }
    }

    public static Camera2BasicFragment newInstance() {
        return new Camera2BasicFragment();
    }


    private void updateActiveModel(){

        synchronized (lock){
            runClassifier = false;
        }

        if (classifier != null){
            classifier.close();
            classifier = null;
        }

        Log.i("INFO", "applying model...");
        backgroundHandler.post(() -> {

            try { //loading model
                classifier = new ImageClassifierQuantizedMobileNet(getActivity());
            } catch (IOException e) {
                Log.e("ERR", "cant load classifier");
                classifier = null;
            }

            if (classifier == null) {
                return;
            }

            classifier.setNumThreads(4); // from 1 to 10, number of threads
        });

        synchronized (lock){
            runClassifier = true;
        }
    }

    private float bitmapSim(Bitmap tocompare){
        getActivity().runOnUiThread(() -> lastview.setImageBitmap(tocompare));
        return 1;
    }

    private void classifyFrame() {
        if (cameraDevice == null || getActivity() == null || classifier == null) {
            return;
        }
        long startTime = SystemClock.uptimeMillis(), endTime;
        Bitmap resized = Bitmap.createBitmap(textureView.getBitmap(), 0, (textureView.getHeight()-textureView.getWidth())/2, textureView.getWidth(), textureView.getWidth());
        Bitmap scaled = Bitmap.createScaledBitmap(resized, 300, 300, false);

        classifier.classifyFrame(scaled);

        float[][] boxes = new float[10][4];
        float[] scores = new float[10];
        float[] classes = new float[10];

        for(int i=0; i<10; i++) {
            System.arraycopy(classifier.getBoxes()[i], 0, boxes[i], 0, 4);
        }
        System.arraycopy(classifier.getClasses(), 0, classes, 0, 10);
        System.arraycopy(classifier.getScores(), 0, scores, 0, 10);

        //Get the results and now: if clicked is set to (-1, -1) then normally show all objects
        //if is set to some kind of value then it means user clicked on object and we need to now on what he/she clicked and then set point to (-2,-2)
        //(-2, -2) means tracking state
        int offset = (textureView.getHeight() - textureView.getWidth()) / 2;
        Paint paintt = new Paint();
        paintt.setColor(Color.BLUE);
        paintt.setTextSize(36);
        if (clicked.x == -1){

            Paint paint = new Paint();
            paint.setStyle(Paint.Style.STROKE);
            paint.setColor(Color.GREEN);

            if(surfaceHolder.getSurface().isValid()) {
                final Canvas canvas1 = surfaceHolder.lockCanvas();
                if (canvas1 != null) {

                    canvas1.drawColor(Color.TRANSPARENT, PorterDuff.Mode.CLEAR);
                    canvas1.drawColor(Color.TRANSPARENT);
                    int i = 0;
                    while (i < 10 && scores[i] >= 0.5){
                        canvas1.drawRect(boxes[i][1] * canvas1.getWidth(), (boxes[i][0] * canvas1.getWidth()) + offset, boxes[i][3] * canvas1.getWidth(), (boxes[i][2] * canvas1.getWidth()) + offset, paint);
                        i++;
                    }
                    //drawing of speed
                    endTime = SystemClock.uptimeMillis();
                    canvas1.drawText(Long.toString(endTime-startTime) + "ms", canvas1.getWidth()-200, 50, paintt);
                    surfaceHolder.unlockCanvasAndPost(canvas1);
                }
            }

        } else if (clicked.x == -2){
            int i = 0;
            boolean matching = false;
            while (i < 10 && scores[i] >= 0.5){
                if(classes[i] != lastid){
                    i++;
                    continue;
                }
                int x = (int)(boxes[i][1] * 300);
                if (x < 0) {x =0;}
                int y = (int)(boxes[i][0] * 300);
                if (y<0) {y=0;}
                int width = (int)(boxes[i][3] * 300) - x;
                if (width+x>300) {width=300-x;}
                int height = (int)(boxes[i][2] * 300) - y;
                if (height+y>300) {height=300-y;}

                Bitmap tocompare = Bitmap.createBitmap(scaled, x, y, width, height);
                if (bitmapSim(tocompare) < 0.2){ //if the difference is smaller than 20%
                    matching = true;
                    break;
                }
                i++;
            }
            if (matching){
                Log.d("INFO", "znaleziono podobny obiekt!"); //now we need to draw shape around it
            } else {
                Log.d("INFO", "nie znaleziono podobnego obiektu");
            }

        } else { //we need to find on what object user clicked and add it to compare base
            boolean found = false;
            if(surfaceHolder.getSurface().isValid()) {
                final Canvas canvas1 = surfaceHolder.lockCanvas();
                if (canvas1 != null) {
                    canvas1.drawColor(Color.TRANSPARENT, PorterDuff.Mode.CLEAR);
                    canvas1.drawColor(Color.TRANSPARENT);
                    float ymax=0, ymin=0, xmax=0, xmin=0;
                    int i=0;
                    while (i < 10 && scores[i] >= 0.5){
                        xmin = boxes[i][1] * canvas1.getWidth();
                        xmax = boxes[i][3] * canvas1.getWidth();
                        ymin = (boxes[i][0] * canvas1.getWidth()) + offset;
                        ymax = (boxes[i][2] * canvas1.getWidth()) + offset;

                        if(clicked.x >= xmin && clicked.x <= xmax && clicked.y >= ymin && clicked.y <= ymax){
                            found = true;
                            break;
                        }
                        i++;
                    }
                    if (found){ //if we found this object then we need to draw and remember what it is
                        Log.d("INFO", "found object id: " + Float.toString(classes[i]+1));
                        lastid = classes[i];

                        Paint paint = new Paint();
                        paint.setStyle(Paint.Style.STROKE);
                        paint.setColor(Color.RED);
                        canvas1.drawRect(xmin, ymin, xmax, ymax, paint);

                        int x = (int)(boxes[i][1] * 300);
                        if (x < 0) {x =0;}
                        int y = (int)(boxes[i][0] * 300);
                        if (y<0) {y=0;}
                        int width = (int)(boxes[i][3] * 300) - x;
                        if (width+x>300) {width=300-x;}
                        int height = (int)(boxes[i][2] * 300) - y;
                        if (height+y>300) {height=300-y;}
                        last = Bitmap.createBitmap(scaled, x, y, width, height); //saving the look of saved object

                        getActivity().runOnUiThread(() -> lastview.setImageBitmap(last));
                        clicked.x = -2;
                        clicked.y = -2;

                    } else { //if not set the point to (-1, -1)
                        Log.e("ERR", "cant find clicked object");
                        clicked.x = -1;
                        clicked.y = -1;
                    }
                    endTime = SystemClock.uptimeMillis();
                    canvas1.drawText(Long.toString(endTime-startTime) + "ms", canvas1.getWidth()-200, 50, paintt);
                    surfaceHolder.unlockCanvasAndPost(canvas1);
                }
            }
        }

        resized.recycle();
        scaled.recycle();
    }

    private Runnable periodicClassify = new Runnable() {
        @Override
        public void run() {
            synchronized (lock){
                if (runClassifier){
                    classifyFrame();
                }
            }
            backgroundHandler.post(periodicClassify);
        }
    };

    private void setUpCamera(int width, int height){
        Activity activity = getActivity();
        if (activity == null || activity.isFinishing())
            return;
        cameraManager = (CameraManager) activity.getSystemService(Context.CAMERA_SERVICE);

        int cameraFacing = CameraCharacteristics.LENS_FACING_BACK;

        try{
            if (!CameraOpenCloseLock.tryAcquire(2500, TimeUnit.MICROSECONDS)){
                throw new RuntimeException("Time out waiting to lock camera opening.");
            }

            for(String cameraId: cameraManager.getCameraIdList()){
                CameraCharacteristics cameraCharacteristics = cameraManager.getCameraCharacteristics(cameraId);
                Integer facing = cameraCharacteristics.get(CameraCharacteristics.LENS_FACING);
                if(facing != null && facing  == cameraFacing){
                    StreamConfigurationMap streamConfigurationMap = cameraCharacteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP);
                    mSensorOrientation = cameraCharacteristics.get(CameraCharacteristics.SENSOR_ORIENTATION);
                    if(streamConfigurationMap == null){
                        continue;
                    }

                    mVideoSize = chooseVideoSize(streamConfigurationMap.getOutputSizes(MediaRecorder.class));
                    previewSize = chooseOptimalSize(streamConfigurationMap.getOutputSizes(SurfaceTexture.class),
                            width, height, mVideoSize);


                    int orientation = getResources().getConfiguration().orientation;
                    if (orientation == Configuration.ORIENTATION_LANDSCAPE) {
                        textureView.setAspectRatio(previewSize.getWidth(), previewSize.getHeight());
                    } else {
                        textureView.setAspectRatio(previewSize.getHeight(), previewSize.getWidth());
                    }

                    //previewSize = streamConfigurationMap.getOutputSizes(SurfaceTexture.class)[0];
                    this.cameraId = cameraId;
                }
            }
        } catch (CameraAccessException e){
            e.printStackTrace();
        } catch (InterruptedException e){
            throw new RuntimeException("Interrupted while trying to lock camera opening.");
        }
    }

    private boolean hasPermissionsGranted(String[] permissions, Activity activity) {
        for (String permission : permissions) {
            if (ActivityCompat.checkSelfPermission(activity, permission)
                    != PackageManager.PERMISSION_GRANTED) {
                return false;
            }
        }
        return true;
    }

    private void openCamera(int width, int height){
        Activity activity = getActivity();
        if (activity == null){
            return;
        }

        if (!hasPermissionsGranted(VIDEO_PERMISSIONS, activity)) {
            ActivityCompat.requestPermissions(activity, VIDEO_PERMISSIONS, CAMERA_REQUEST_CODE);
            return;
        }

        setUpCamera(width, height);
        configureTransform(width, height);

        mMediaRecorder = new MediaRecorder();

        try {
            cameraManager.openCamera(cameraId, stateCallback, backgroundHandler); //when set to null works badly
        } catch (CameraAccessException e){
            e.printStackTrace();
        } catch (SecurityException e){
            Log.e("ERR", "No permissions");
        }
    }

    private void openBackgroundThread() {
        backgroundThread = new HandlerThread("camera_background_thread");
        backgroundThread.start();
        backgroundHandler = new Handler(backgroundThread.getLooper());
        synchronized (lock){
            runClassifier = true;
        }
        backgroundHandler.post(periodicClassify);
    }

    private void createPreviewSession() {
        if (cameraDevice == null || !textureView.isAvailable() || previewSize == null){
            return;
        }

        try {
            closePreviewSession();
            SurfaceTexture surfaceTexture = textureView.getSurfaceTexture();
            assert surfaceTexture != null;
            surfaceTexture.setDefaultBufferSize(previewSize.getWidth(), previewSize.getHeight());


            Surface previewSurface = new Surface(surfaceTexture);
            captureRequestBuilder = cameraDevice.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);
            captureRequestBuilder.addTarget(previewSurface);

            ViewGroup.LayoutParams lp = new RelativeLayout.LayoutParams(textureView.getWidth(), textureView.getHeight());
            surfaceView.setLayoutParams(lp);

            cameraDevice.createCaptureSession(Collections.singletonList(previewSurface), new CameraCaptureSession.StateCallback() {
                @Override
                public void onConfigured(@NonNull CameraCaptureSession session) {
                    cameraCaptureSession = session;
                    updatePreview(); //ADDED
                }

                @Override
                public void onConfigureFailed(@NonNull CameraCaptureSession cameraCaptureSession) {
                    Activity activity = getActivity();
                    if (null != activity){
                        Toast.makeText(activity, "Failed", Toast.LENGTH_SHORT).show(); //ZM
                    }
                }
            }, backgroundHandler);
        } catch (CameraAccessException e){
            e.printStackTrace();
        }
    }

    private void updatePreview() {
        if (cameraDevice == null){
            return;
        }

        try {
            captureRequestBuilder.set(CaptureRequest.CONTROL_MODE, CameraMetadata.CONTROL_MODE_AUTO); //Errors with camera only with huawei
            HandlerThread thread = new HandlerThread("CameraPreview");
            thread.start();
            captureRequest = captureRequestBuilder.build();
            cameraCaptureSession.setRepeatingRequest(captureRequest, null, backgroundHandler);
        } catch (CameraAccessException e){
            e.printStackTrace();
        }
    }

    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        return inflater.inflate(R.layout.camera2_basic, container, false);
    }

    @Override
    public void onViewCreated(@NonNull final View view, Bundle savedInstanceState) {
        textureView = view.findViewById(R.id.texture);
        textureView.setOnTouchListener(touchListener);

        surfaceView = view.findViewById(R.id.surfaceView);
        surfaceView.setZOrderOnTop(true);
        surfaceHolder = surfaceView.getHolder();
        surfaceHolder.setFormat(PixelFormat.TRANSPARENT);

        mButtonVideo = view.findViewById(R.id.video);
        mButtonVideo.setOnClickListener(this);

        resetButton = view.findViewById(R.id.reset);
        resetButton.setOnClickListener(this);

        lastview = view.findViewById(R.id.imageview);
    }

    View.OnTouchListener touchListener = new View.OnTouchListener() { //if clicked it throws coordinates only when before clicked=(-1,-1)
        @Override
        public boolean onTouch(View v, MotionEvent event) {
            if(clicked.x == -1) {
                clicked.x = (int) event.getX();
                clicked.y = (int) event.getY();
            }
            return false;
        }
    };

    @Override
    public void onResume(){
        super.onResume();
        openBackgroundThread();
        updateActiveModel();
        if (textureView.isAvailable()){
            openCamera(textureView.getWidth(), textureView.getHeight());
        } else {
            textureView.setSurfaceTextureListener(surfaceTextureListener);
        }
    }

    @Override
    public void onStop(){
        super.onStop();
        closeCamera();
        closeBackgroundThread();
    }

    @Override
    public void onPause(){  //ADDED
        closeCamera();
        closeBackgroundThread();
        super.onPause();
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.video: {
                if (mIsRecordingVideo) {
                    stopRecordingVideo();
                } else {
                    startRecordingVideo();
                }
                break;
            }
            case R.id.reset: {
                clicked.x = -1;
                clicked.y = -1;
                break;
            }
        }
    }

    private void closeCamera(){
        try {
            CameraOpenCloseLock.acquire();
            closePreviewSession(); //ADDED
            if (cameraDevice != null) {
                cameraDevice.close();
                cameraDevice = null;
            }
            if (null != mMediaRecorder) {
                mMediaRecorder.release();
                mMediaRecorder = null;
            }
        } catch (InterruptedException e) {
            throw new RuntimeException("Interrupted while trying to lock camera closing.");
        } finally {
            CameraOpenCloseLock.release();
        }
    }

    private void closeBackgroundThread(){
        if (backgroundHandler != null) {
            backgroundThread.quitSafely();
            try {
                backgroundThread.join();
                backgroundThread = null;
                backgroundHandler = null;
                synchronized (lock) {
                    runClassifier = false;
                }
            } catch (InterruptedException e) {
                Log.d("TAG", "Interrupted when stopping background thread", e);
            }
        }
    }

    private void configureTransform (int viewWidth, int viewHeight) {
        Activity activity = getActivity();
        if (textureView == null || previewSize == null || activity == null) {
            return;
        }
        int rotation = activity.getWindowManager().getDefaultDisplay().getRotation();
        Matrix matrix = new Matrix();
        RectF viewRect = new RectF(0, 0, viewWidth, viewHeight);
        RectF bufferRect = new RectF(0, 0, previewSize.getHeight(), previewSize.getWidth());
        float centerX = viewRect.centerX();
        float centerY = viewRect.centerY();
        if (Surface.ROTATION_90 == rotation || Surface.ROTATION_270 == rotation) {
            bufferRect.offset(centerX - bufferRect.centerX(), centerY = bufferRect.centerY());
            matrix.setRectToRect(viewRect, bufferRect, Matrix.ScaleToFit.FILL);
            float scale = Math.max(
                    (float) viewHeight / previewSize.getHeight(),
                    (float) viewWidth / previewSize.getWidth());
            matrix.postScale(scale, scale, centerX, centerY);
            matrix.postRotate(90 * (rotation - 2), centerX, centerY);
        } else if (Surface.ROTATION_180 == rotation) {
            matrix.postRotate(180, centerX, centerY);
        }

        activity.runOnUiThread(() -> textureView.setTransform(matrix));
    }

    static class CompareSizesByArea implements Comparator<Size> {

        @Override
        public int compare(Size lhs, Size rhs) {
            // We cast here to ensure the multiplications won't overflow
            return Long.signum((long) lhs.getWidth() * lhs.getHeight() -
                    (long) rhs.getWidth() * rhs.getHeight());
        }

    }

    private void closePreviewSession() {
        if (cameraCaptureSession != null){
            cameraCaptureSession.close();
            cameraCaptureSession = null;
        }
    }


    private void setUpMediaRecorder() throws IOException {
        final Activity activity = getActivity();
        if (null == activity) {
            return;
        }
        mMediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        mMediaRecorder.setVideoSource(MediaRecorder.VideoSource.SURFACE);
        mMediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
        if (mNextVideoAbsolutePath == null || mNextVideoAbsolutePath.isEmpty()) {
            mNextVideoAbsolutePath = getVideoFilePath(getActivity());
        }
        mMediaRecorder.setOutputFile(mNextVideoAbsolutePath);
        mMediaRecorder.setVideoEncodingBitRate(10000000);
        mMediaRecorder.setVideoFrameRate(30);
        mMediaRecorder.setVideoSize(mVideoSize.getWidth(), mVideoSize.getHeight());
        mMediaRecorder.setVideoEncoder(MediaRecorder.VideoEncoder.H264);
        mMediaRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
        mMediaRecorder.setAudioSamplingRate(16000); //dodalem
        int rotation = activity.getWindowManager().getDefaultDisplay().getRotation();
        switch (mSensorOrientation) {
            case SENSOR_ORIENTATION_DEFAULT_DEGREES:
                mMediaRecorder.setOrientationHint(DEFAULT_ORIENTATIONS.get(rotation));
                break;
            case SENSOR_ORIENTATION_INVERSE_DEGREES:
                mMediaRecorder.setOrientationHint(INVERSE_ORIENTATIONS.get(rotation));
                break;
        }
        mMediaRecorder.prepare();
    }

    private String getVideoFilePath(Context context) {
        final File dir = context.getExternalFilesDir(null);
        return (dir == null ? "" : (dir.getAbsolutePath() + "/"))
                + System.currentTimeMillis() + ".mp4";
    }

    private void startRecordingVideo() {
        if (null == cameraDevice || !textureView.isAvailable() || null == previewSize) {
            return;
        }
        try {
            closePreviewSession();
            setUpMediaRecorder();
            SurfaceTexture texture = textureView.getSurfaceTexture();
            assert texture != null;
            texture.setDefaultBufferSize(previewSize.getWidth(), previewSize.getHeight());
            captureRequestBuilder = cameraDevice.createCaptureRequest(CameraDevice.TEMPLATE_RECORD);
            List<Surface> surfaces = new ArrayList<>();

            // Set up Surface for the camera preview
            Surface previewSurface = new Surface(texture);
            surfaces.add(previewSurface);
            captureRequestBuilder.addTarget(previewSurface);

            // Set up Surface for the MediaRecorder
            Surface recorderSurface = mMediaRecorder.getSurface();
            surfaces.add(recorderSurface);
            captureRequestBuilder.addTarget(recorderSurface);

            // Start a capture session
            // Once the session starts, we can update the UI and start recording
            cameraDevice.createCaptureSession(surfaces, new CameraCaptureSession.StateCallback() {

                @Override
                public void onConfigured(@NonNull CameraCaptureSession cameraCaptureSession) {
                    Camera2BasicFragment.this.cameraCaptureSession = cameraCaptureSession;
                    updatePreview(); //ZM
                    getActivity().runOnUiThread(() -> {

                            mButtonVideo.setText(R.string.stop);
                            mIsRecordingVideo = true;

                            // Start recording
                            mMediaRecorder.start();
                            Log.d("INFO", "recording started");
                    });
                }

                @Override
                public void onConfigureFailed(@NonNull CameraCaptureSession cameraCaptureSession) {
                    Activity activity = getActivity();
                    if (null != activity) {
                        Toast.makeText(activity, "Failed", Toast.LENGTH_SHORT).show();
                    }
                }
            }, backgroundHandler);
        } catch (CameraAccessException | IOException e) {
            e.printStackTrace();
        }

    }

    private void stopRecordingVideo() {
        // UI
        mIsRecordingVideo = false;
        mButtonVideo.setText(R.string.record);
        // Stop recording
        try {
            mMediaRecorder.stop();
        } catch (RuntimeException stopException){
            Log.d("INFO", "Error with recording");
        }
        mMediaRecorder.reset();

        Activity activity = getActivity();
        if (null != activity) {
            Toast.makeText(activity, "Video saved: " + mNextVideoAbsolutePath,
                    Toast.LENGTH_SHORT).show();
            Log.d("TAG", "Video saved: " + mNextVideoAbsolutePath);
        }
        mNextVideoAbsolutePath = null;
        createPreviewSession();
    }

}