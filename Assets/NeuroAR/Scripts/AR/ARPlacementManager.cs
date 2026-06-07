using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;
using System.Collections.Generic;

namespace NeuroAR.AR
{
    public class ARPlacementManager : MonoBehaviour
    {
        [Header("Références")]
        public GameObject networkRootPrefab;
        public ARRaycastManager raycastManager;
        public ARPlaneManager planeManager;

        [Header("UI")]
        public GameObject placementIndicator;

        [Header("Config")]
        public float scaleFactor = 1f;

        private GameObject _spawnedNetwork;
        private bool _isPlaced = false;
        private List<ARRaycastHit> _hits = new();
        private Pose _placementPose;
        private bool _placementPoseIsValid = false;

        void Update()
        {
            if (_isPlaced) return;

            UpdatePlacementPose();
            UpdatePlacementIndicator();

            if (_placementPoseIsValid && Input.touchCount > 0)
            {
                Touch touch = Input.GetTouch(0);
                if (touch.phase == TouchPhase.Began)
                    PlaceNetwork();
            }
        }

        private void UpdatePlacementPose()
        {
            Vector2 screenCenter = new Vector2(
                Screen.width / 2f,
                Screen.height / 2f
            );

            _placementPoseIsValid = raycastManager.Raycast(
                screenCenter,
                _hits,
                TrackableType.PlaneWithinPolygon
            );

            if (_placementPoseIsValid)
                _placementPose = _hits[0].pose;
        }

        private void UpdatePlacementIndicator()
        {
            if (placementIndicator == null) return;

            placementIndicator.SetActive(_placementPoseIsValid);

            if (_placementPoseIsValid)
            {
                placementIndicator.transform.SetPositionAndRotation(
                    _placementPose.position,
                    _placementPose.rotation
                );
            }
        }

        private void PlaceNetwork()
        {
            if (networkRootPrefab == null) return;

            _spawnedNetwork = Instantiate(
                networkRootPrefab,
                _placementPose.position,
                _placementPose.rotation
            );

            _spawnedNetwork.transform.localScale =
                Vector3.one * scaleFactor;

            _isPlaced = true;

            // Cache les plans AR après placement
            SetPlanesActive(false);

            if (placementIndicator != null)
                placementIndicator.SetActive(false);
        }

        private void SetPlanesActive(bool active)
        {
            foreach (var plane in planeManager.trackables)
                plane.gameObject.SetActive(active);

            planeManager.enabled = active;
        }

        public void ResetPlacement()
        {
            if (_spawnedNetwork != null)
                Destroy(_spawnedNetwork);

            _isPlaced = false;
            SetPlanesActive(true);
            planeManager.enabled = true;

            if (placementIndicator != null)
                placementIndicator.SetActive(true);
        }

        public GameObject GetSpawnedNetwork() => _spawnedNetwork;
        public bool IsPlaced => _isPlaced;
    }
}