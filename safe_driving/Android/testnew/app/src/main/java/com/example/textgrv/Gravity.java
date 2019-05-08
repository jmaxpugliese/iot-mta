package com.example.textgrv;

import java.io.RandomAccessFile;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;

import com.amazonaws.mobile.client.Callback;
import com.amazonaws.mobile.client.UserStateDetails;
import com.amazonaws.mobileconnectors.kinesis.kinesisrecorder.*;
import com.amazonaws.mobile.client.AWSMobileClient;
import com.amazonaws.regions.Regions;

import android.os.Bundle;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.StrictMode;
import android.support.v7.app.AppCompatActivity;
import java.io.File;
import android.os.Environment;
import android.util.Log;
import android.view.KeyEvent;
import android.widget.CompoundButton;
import android.widget.CompoundButton.OnCheckedChangeListener;
import android.widget.Switch;

import static android.provider.ContactsContract.CommonDataKinds.StructuredPostal.REGION;

public class Gravity extends AppCompatActivity implements SensorEventListener {

    private SensorManager sensorManager;
    private Sensor accelerometer;
    private Switch gSwitch;
    private String fileName;
    private ArrayList<String> res;
    private int count;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (android.os.Build.VERSION.SDK_INT > 9) {
            StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
            StrictMode.setThreadPolicy(policy);
        }
        AWSMobileClient.getInstance().initialize(getApplicationContext(), new Callback<UserStateDetails>() {
                    @Override
                    public void onResult(UserStateDetails userStateDetails) {
                        Log.i("INIT", userStateDetails.getUserState().toString());
                    }

                    @Override
                    public void onError(Exception e) {
                        Log.e("INIT", "Initialization error.", e);
                    }
                }
        );
        sensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);
        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION);
        count = 0;
        gSwitch = (Switch) findViewById(R.id.gswitch);
        gSwitch.setOnCheckedChangeListener(new gOnCheckChangeListener());
        res = new ArrayList<>();
        /*SimpleDateFormat sdf = new SimpleDateFormat("HHmmss");
        try {
            File sdCardDir = Environment.getExternalStorageDirectory();
            fileName = sdCardDir.getCanonicalPath() + "/acc_" + sdf.format(new Date()) + ".txt";
            writeFileSdcard(count++ + "\n");
        } catch (Exception e) {
            e.printStackTrace();
        }*/
        //fileName = "acc_" + sdf.format(new Date()) + ".txt";
    }

    class gOnCheckChangeListener implements OnCheckedChangeListener {

        @Override
        public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
            // TODO Auto-generated method stub
            if (isChecked) {
                sensorManager.registerListener(Gravity.this, accelerometer, SensorManager.SENSOR_DELAY_NORMAL);
            } else {
                sensorManager.unregisterListener(Gravity.this);
            }
        }

    }

    @Override
    protected void onRestart() {
        // TODO Auto-generated method stub
        super.onRestart();
        sensorManager.registerListener(Gravity.this, accelerometer, SensorManager.SENSOR_DELAY_NORMAL);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_VOLUME_DOWN) {
            sensorManager.registerListener(Gravity.this, accelerometer, SensorManager.SENSOR_DELAY_NORMAL);
            return true;
        } else return super.onKeyDown(keyCode, event);
    }

    @Override
    public boolean onKeyUp(int keyCode, KeyEvent event) {
        // TODO Auto-generated method stub
        if (keyCode == KeyEvent.KEYCODE_VOLUME_DOWN  ) {
            //writeFileSdcard(count++ + "\n");
            sensorManager.unregisterListener(Gravity.this);
            return true;
        } else return super.onKeyUp(keyCode, event);
    }

    @Override
    public void onAccuracyChanged(Sensor arg0, int arg1) {

    }

    @Override
    public void onSensorChanged(SensorEvent event) {

        /*
        float x = event.values[0];
        float y = event.values[1];
        float z = event.values[2];

        System.out.println("x----->" + x);
        System.out.println("y----->" + y);
        System.out.println("z----->" + z);
        String message = new String();
        */

        float X = event.values[0];
        float Y = event.values[1];
        float Z = event.values[2];
        res.add(Float.toString(X));
        res.add(Float.toString(Y));
        res.add(Float.toString(Z));
        if(res.size() == 15) {
            sendToKensis(res);
            res.clear();
        }

        /*DecimalFormat df = new DecimalFormat("#,##0.000");
        SimpleDateFormat sdf = new SimpleDateFormat("HH:mm:ss");
        String str = sdf.format(new Date());
        //message = str + "\n";
        message += df.format(X) + "  ";
        message += df.format(Y) + "  ";
        message += df.format(Z) + "\n";
        writeFileSdcard(message);*/
    }

    public void sendToKensis(ArrayList<String> res) {
        String kinesisDirectory = "Acc-Data";
        KinesisRecorder recorder = new KinesisRecorder(
                Gravity.this.getDir(kinesisDirectory, 0),
                Regions.US_EAST_1,
                AWSMobileClient.getInstance()
        );
        String res_str= String.join(",", res);
        System.out.println(res_str);
        recorder.saveRecord(res_str.getBytes(), "iot-phone-detect");
        recorder.submitAllRecords();
    }

    /*
    public void writeFileSdcard(String message) {
        try {
            if (Environment.getExternalStorageState().equals(Environment.MEDIA_MOUNTED)) {
                //File sdCardDir = Environment.getExternalStorageDirectory();
                File targitFile = new File(fileName);
                RandomAccessFile raf = new RandomAccessFile(targitFile, "rw");
                raf.seek(targitFile.length());
                raf.write(message.getBytes());
                raf.close();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        try {
            FileOutputStream fout = openFileOutput(fileName, Context.MODE_APPEND);
            byte[] bytes = message.getBytes();

            fout.write(bytes);
            fout.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }*/
}