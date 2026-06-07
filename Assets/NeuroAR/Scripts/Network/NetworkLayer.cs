using UnityEngine;
using System.Collections.Generic;

namespace NeuroAR.Network
{
    public class NetworkLayer : MonoBehaviour
    {
        [Header("Config")]
        public int layerIndex;
        public NeuronVisual.NeuronType layerType;
        public int neuronCount;

        [Header("Prefabs")]
        public GameObject neuronPrefab;

        [Header("Layout")]
        public float spacing = 0.15f;

        private List<NeuronVisual> _neurons = new();
        public List<NeuronVisual> Neurons => _neurons;

        public void Build(LayerData data, GameObject prefab)
        {
            neuronPrefab = prefab;
            layerIndex   = data.layerIndex;
            neuronCount  = data.neurons.Count;

            layerType = data.layerType switch
            {
                "input"  => NeuronVisual.NeuronType.Input,
                "output" => NeuronVisual.NeuronType.Output,
                _        => NeuronVisual.NeuronType.Hidden
            };

            SpawnNeurons(data);
        }

        private void SpawnNeurons(LayerData data)
        {
            // Centrage vertical
            float totalHeight = (neuronCount - 1) * spacing;
            float startY      = totalHeight / 2f;

            for (int i = 0; i < neuronCount; i++)
            {
                Vector3 localPos = new Vector3(0, startY - i * spacing, 0);
                GameObject obj   = Instantiate(neuronPrefab, transform);
                obj.transform.localPosition = localPos;
                obj.name = $"Neuron_{layerIndex}_{i}";

                NeuronVisual visual = obj.GetComponent<NeuronVisual>();
                visual.layerIndex  = layerIndex;
                visual.neuronIndex = i;
                visual.SetType(layerType);

                _neurons.Add(visual);
            }
        }

        public void UpdateActivations(LayerData data)
        {
            for (int i = 0; i < _neurons.Count && i < data.neurons.Count; i++)
            {
                _neurons[i].Activate(data.neurons[i].activationValue);
                _neurons[i].SetActivationValue(data.neurons[i].activationValue);
            }
        }

        public NeuronVisual GetNeuron(int index)
        {
            if (index < 0 || index >= _neurons.Count) return null;
            return _neurons[index];
        }
    }
}