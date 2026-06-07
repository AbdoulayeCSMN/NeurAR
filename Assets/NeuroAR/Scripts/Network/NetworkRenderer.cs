using UnityEngine;
using System.Collections;
using System.Collections.Generic;

namespace NeuroAR.Network
{
    public class NetworkRenderer : MonoBehaviour
    {
        [Header("Prefabs")]
        public GameObject neuronPrefab;
        public GameObject connectionPrefab;

        [Header("Layout")]
        public float layerSpacing  = 0.25f;
        public float animDelay     = 0.05f;

        private List<NetworkLayer>     _layers      = new();
        private List<ConnectionVisual> _connections = new();
        private NetworkData            _currentData;

        public void BuildNetwork(NetworkData data)
        {
            ClearNetwork();
            _currentData = data;

            float totalWidth = (data.totalLayers - 1) * layerSpacing;
            float startX     = -totalWidth / 2f;

            // Spawn layers
            foreach (var layerData in data.layers)
            {
                GameObject layerObj = new GameObject($"Layer_{layerData.layerIndex}");
                layerObj.transform.SetParent(transform);
                layerObj.transform.localPosition = new Vector3(
                    startX + layerData.layerIndex * layerSpacing, 0, 0
                );

                NetworkLayer layer = layerObj.AddComponent<NetworkLayer>();
                layer.Build(layerData, neuronPrefab);
                _layers.Add(layer);
            }

            // Spawn connections
            BuildConnections(data);
        }

        private void BuildConnections(NetworkData data)
        {
            for (int l = 0; l < _layers.Count - 1; l++)
            {
                NetworkLayer layerA = _layers[l];
                NetworkLayer layerB = _layers[l + 1];

                LayerData dataB = data.layers[l + 1];
                int weightIdx   = 0;

                foreach (var nA in layerA.Neurons)
                {
                    foreach (var nB in layerB.Neurons)
                    {
                        GameObject connObj = Instantiate(
                            connectionPrefab, transform
                        );
                        connObj.name = $"Conn_{l}_{nA.neuronIndex}_{nB.neuronIndex}";

                        ConnectionVisual conn = connObj.GetComponent<ConnectionVisual>();
                        conn.neuronA = nA.transform;
                        conn.neuronB = nB.transform;

                        float w = (weightIdx < dataB.weights.Count)
                            ? dataB.weights[weightIdx++]
                            : 0f;
                        conn.SetWeight(w);

                        _connections.Add(conn);
                    }
                }
            }
        }

        public void UpdateNetwork(NetworkData data)
        {
            _currentData = data;
            for (int i = 0; i < _layers.Count && i < data.layers.Count; i++)
                _layers[i].UpdateActivations(data.layers[i]);

            if (data.phase == "forward")
                StartCoroutine(AnimateForwardPass());
            else if (data.phase == "backward")
                StartCoroutine(AnimateBackwardPass());
        }

        private IEnumerator AnimateForwardPass()
        {
            foreach (var layer in _layers)
            {
                foreach (var neuron in layer.Neurons)
                    neuron.Activate(neuron.activationValue);

                // Anime les connections sortantes
                foreach (var conn in _connections)
                    if (conn.neuronA != null)
                        conn.AnimateActivation(0.3f);

                yield return new WaitForSeconds(animDelay);
            }
        }

        private IEnumerator AnimateBackwardPass()
        {
            for (int i = _layers.Count - 1; i >= 0; i--)
            {
                foreach (var neuron in _layers[i].Neurons)
                    neuron.Activate(neuron.activationValue);

                yield return new WaitForSeconds(animDelay);
            }
        }

        public void ClearNetwork()
        {
            foreach (Transform child in transform)
                Destroy(child.gameObject);

            _layers.Clear();
            _connections.Clear();
        }
    }
}