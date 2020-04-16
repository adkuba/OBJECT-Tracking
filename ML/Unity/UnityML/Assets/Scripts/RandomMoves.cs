using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RandomMoves : MonoBehaviour
{
    private Vector3 newPos;
    private Vector3 lastPos;
    private float speed;

    void Start()
    {
        newPos = transform.position;
        speed = Random.Range(3f, 6f);
    }

    void Update()
    {
        if (Vector3.Distance(transform.position, newPos) < 0.001f)
        {
            genNewPos();
        }
        else
        {
            float step = speed * Time.deltaTime;
            transform.position = Vector3.MoveTowards(transform.position, newPos, step);
        }
        if (transform.position.x >= -2 && transform.position.x <= 2 && transform.position.z >= -2 && transform.position.z <= 2)
        {
            //odbijamy od kamery
            newPos = lastPos;
        }
    }

    void genNewPos()
    {
        float x = Random.Range(-25f, 25f);
        float z = Random.Range(-25f, 25f);
        lastPos = newPos;
        newPos = new Vector3(x, transform.position.y, z);
        speed = Random.Range(3f, 6f);
    }
}
