using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GameController : MonoBehaviour
{
    public GameObject[] objectsPrefab;
    private GameObject tracked;
    private List<GameObject> allObjects = new List<GameObject>();
    private GameObject mainCamera;
    private GameObject parent;

    void Start()
    {
        parent = transform.parent.gameObject;
        mainCamera = parent.transform.GetChild(1).gameObject;
        Restart();
    }

    public void Restart()
    {
        //usuwamy
        foreach(GameObject obj in allObjects)
        {
            Destroy(obj);
        }
        allObjects.Clear();
        mainCamera.transform.eulerAngles = new Vector3(0f, 0f, 0f);

        //wybieramy sledzony i ustawiamy przed kamera
        tracked = Instantiate(objectsPrefab[Random.Range(0, objectsPrefab.Length)]) as GameObject;
        tracked.transform.parent = parent.transform;
        tracked.transform.localPosition = new Vector3(0, tracked.transform.position.y, 6);
        allObjects.Add(tracked);

        //ustawiamy pozostale obiekty
        foreach (GameObject obj in objectsPrefab)
        {
            //od 0 do 3
            int counter = Random.Range(0, 4);
            for (int i = 0; i < counter; i++)
            {
                GameObject o = Instantiate(obj) as GameObject;
                o.transform.parent = parent.transform;
                allObjects.Add(o);
                //pos offset
                o.transform.localPosition = new Vector3(o.transform.position.x, o.transform.position.y, o.transform.position.z - i * 5f);
            }
        }
    }

    public float getAngle()
    {
        //tu nie musi byc local position
        Vector3 camOnGround = new Vector3(mainCamera.transform.position.x, 0, mainCamera.transform.position.z);
        Vector3 targetDir = new Vector3(tracked.transform.position.x, 0, tracked.transform.position.z) - camOnGround;
        Vector3 camForwardOnGround = new Vector3(mainCamera.transform.forward.x, 0, mainCamera.transform.forward.z);
        return Vector3.SignedAngle(targetDir, camForwardOnGround, Vector3.up);
    }
}
