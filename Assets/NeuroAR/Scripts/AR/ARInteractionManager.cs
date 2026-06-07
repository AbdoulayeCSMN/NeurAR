using UnityEngine;
using NeuroAR.Network;

namespace NeuroAR.AR
{
    public class ARInteractionManager : MonoBehaviour
    {
        [Header("Références")]
        public ARPlacementManager placementManager;
        public Camera arCamera;

        [Header("Config")]
        public float rotationSpeed = 0.3f;
        public float scaleMin      = 0.3f;
        public float scaleMax      = 3f;

        private GameObject _network;
        private Vector2 _lastTouchPos;
        private float _initialPinchDistance;
        private float _initialScale;
        private NeuronVisual _selectedNeuron;

        void Update()
        {
            if (!placementManager.IsPlaced) return;

            _network = placementManager.GetSpawnedNetwork();
            if (_network == null) return;

            HandleTouch();
        }

        private void HandleTouch()
        {
            // Un seul doigt → rotation
            if (Input.touchCount == 1)
            {
                Touch touch = Input.GetTouch(0);

                if (touch.phase == TouchPhase.Began)
                {
                    _lastTouchPos = touch.position;
                    TrySelectNeuron(touch.position);
                }
                else if (touch.phase == TouchPhase.Moved)
                {
                    Vector2 delta = touch.position - _lastTouchPos;
                    RotateNetwork(delta);
                    _lastTouchPos = touch.position;
                }
            }

            // Deux doigts → pinch to zoom
            else if (Input.touchCount == 2)
            {
                Touch t0 = Input.GetTouch(0);
                Touch t1 = Input.GetTouch(1);

                if (t0.phase == TouchPhase.Began || t1.phase == TouchPhase.Began)
                {
                    _initialPinchDistance = Vector2.Distance(t0.position, t1.position);
                    _initialScale         = _network.transform.localScale.x;
                }
                else if (t0.phase == TouchPhase.Moved || t1.phase == TouchPhase.Moved)
                {
                    float currentDist = Vector2.Distance(t0.position, t1.position);
                    float scaleFactor = currentDist / _initialPinchDistance;
                    float newScale    = Mathf.Clamp(
                        _initialScale * scaleFactor,
                        scaleMin,
                        scaleMax
                    );
                    _network.transform.localScale = Vector3.one * newScale;
                }
            }
        }

        private void RotateNetwork(Vector2 delta)
        {
            _network.transform.Rotate(
                Vector3.up,
                -delta.x * rotationSpeed,
                Space.World
            );
        }

        private void TrySelectNeuron(Vector2 screenPos)
        {
            Ray ray = arCamera.ScreenPointToRay(screenPos);
            if (Physics.Raycast(ray, out RaycastHit hit, 10f))
            {
                NeuronVisual neuron = hit.collider.GetComponent<NeuronVisual>();
                if (neuron != null)
                {
                    SelectNeuron(neuron);
                }
            }
        }

        private void SelectNeuron(NeuronVisual neuron)
        {
            // Désélectionne le précédent
            if (_selectedNeuron != null)
                _selectedNeuron.transform.localScale = Vector3.one;

            _selectedNeuron = neuron;
            _selectedNeuron.transform.localScale = Vector3.one * 1.5f;

            Debug.Log($"Neuron sélectionné : Layer {neuron.layerIndex} " +
                      $"Index {neuron.neuronIndex} " +
                      $"Activation {neuron.activationValue:F4}");
        }
    }
}