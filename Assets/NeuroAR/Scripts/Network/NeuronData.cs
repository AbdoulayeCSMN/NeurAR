using System;
using System.Collections.Generic;

namespace NeuroAR.Network
{
    [Serializable]
    public class NeuronData
    {
        public int layerIndex;
        public int neuronIndex;
        public float activationValue;
        public float biasValue;
        public string activationFunction;
    }

    [Serializable]
    public class LayerData
    {
        public int layerIndex;
        public string layerType; // "input", "hidden", "output"
        public List<NeuronData> neurons = new();
        public List<float> weights = new();
    }

    [Serializable]
    public class NetworkData
    {
        public string modelName;
        public int totalLayers;
        public List<LayerData> layers = new();
        public string phase; // "forward", "backward", "idle"
        public float loss;
        public float accuracy;
    }
}