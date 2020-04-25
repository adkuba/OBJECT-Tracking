using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using MLAgents;
using MLAgents.Sensors;

public class CameraAgent : Agent
{
    private GameObject gameController;
    private GameObject parent;
    private float speed = 20;
    private float startTime;

    void Start()
    {
        //pobieramy z rodzica kamery pierwszy obiekt
        parent = transform.parent.gameObject;
        gameController = parent.transform.GetChild(0).gameObject;
    }

    //przed rozpoczeciem iteracji
    public override void OnEpisodeBegin()
    {
        //resetujemy srodowisko
        gameController.GetComponent<GameController>().Restart();
        startTime = Time.time;
    }

    public void MoveCamera(float[] act)
    {
        //przy wartosci <1,2) obraca sie w prawo, przy <2, 3) w lewo,  przy <0, 1) nic nie robi
        var rotation = 0f;
        var action = Mathf.FloorToInt(act[0]);
        switch (action)
        {
            case 1:
                rotation = 1f;
                break;
            case 2:
                rotation = 2f;
                break;
            case 3:
                rotation = -1f;
                break;
            case 4:
                rotation = -2f;
                break;
        }
        transform.Rotate(Vector3.up, rotation * speed * Time.deltaTime, Space.World);
    }

    public override void OnActionReceived(float[] vectorAction)
    {
        MoveCamera(vectorAction);
        
        float angle = gameController.GetComponent<GameController>().getAngle();
        angle = Mathf.Abs(angle);

        //celujemy w srodek obiektu dostajemy nagrode
        if (angle <= 5f)
        {
            AddReward(0.1f);
        }
        //nie celujemy w srodek, dostajemy kare
        //else
        //{
            //AddReward(-0.1f);
        //}
        //max odchylenie 90 stopni
        if (angle >= 90)
        {
            EndEpisode();
        }
        //jesli sledzimy od minuty to konczymy
        if (Time.time - startTime > 60)
        {
            EndEpisode();
        }
    }

    public override float[] Heuristic()
    {
        //dla demo
        float angle = gameController.GetComponent<GameController>().getAngle();

        if (angle < -5 && angle > -20)
        {
            return new float[] { 1 };
        }
        //szybszy ruch
        if (angle <= -20)
        {
            return new float[] { 2 };
        }
        if (angle > 5 && angle < 20)
        {
            return new float[] { 3 };
        }
        //szybszy ruch
        if (angle >= 20)
        {
            return new float[] { 4 };
        }
        return new float[] { 0 };
    }
}
