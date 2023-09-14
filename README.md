# 2023 experiment: Human-Robot Interaction(HRI) Study

## 1. Overview

This repository contains the source code and datasets used for our research project on human-robot interaction in the cooperative game "Don't Starve Together". Our research emphasizes the importance of understanding human social cognition, particularly the attribution of intelligence and agency, in interactions with artificial agents.

## 2. Background

The overarching goal of this project is to use human-robot interaction (HRI) experiments to develop a better understanding of human social cognition, especially the attribution of intelligence and agency. Despite the appearance of "intelligent" behavior, most individuals can discern the difference between interacting with another human and an artificial agent. This project aims to understand the triggers for such recognition, potentially leading to the creation of more "life-like" interactive AI in the future.

## 3. Research Objective

The primary objective is to understand how humans naturally interact in a social environment and to use this information to adopt a data-driven approach for the development of the Social AI. This will elucidate components of the social interaction that affect social fluidity in this environment.

## 4. Hypotheses

This project aims to test several hypotheses, but the repository currently contains source code for:

- **H1 (Turn-Taking Prediction)**: Test the effect of the Social AI avatar's ability to predict when it's their turn to speak.
- **H2 (Repeated Language Code-Switching)**: Examine the effect of repeated language code-switching during a single experiment.

## 5. Game Environment

The experiments utilize a customized version of the video game "Don't Starve Together". The game is a social survival game where players need to collect resources, make tools, fight monsters, and cooperate with each other.

## 6. Research Paper
### Real-Time Multimodal Turn-taking Prediction to Enhance Cooperative Dialogue during Human-Agent Interaction

- **Authors**: Young-Ho Bae, Casey C. Bennett
- **Publication Year**: 2023 August
- **Conference**: 2023 32nd IEEE International Conference on Robot and Human Interactive Communication (RO-MAN)
- **Abstract**:
  Predicting when it is an artificial agent’s turn to speak/act during human-agent interaction (HAI) poses a significant challenge due to the necessity of real-time processing, context sensitivity, capturing complex human behavior, effectively integrating multiple modalities, and addressing class imbalance. In this paper, we present a novel deep learning network-based approach for predicting turn-taking events in HAI that leverages information from multiple modalities, including text, audio, vision, and context data. Our study demonstrates that incorporating additional modalities, including in-game context data, enables a more comprehensive understanding of interaction dynamics leading to enhanced prediction accuracy for the artificial agent. The efficiency of the model also permits potential real-time applications. We evaluated our proposed model on an imbalanced dataset of both successful and failed turn-taking attempts during an HAI cooperative gameplay scenario, comprising over 125,000 instances, and employed a focal loss function to address class imbalance. Our model outperformed baseline models, such as Early Fusion LSTM (EF-LSTM), Late Fusion LSTM (LF-LSTM), and the state-of-the-art Multimodal Transformer (Mult). Additionally, we conducted an ablation study to investigate the contributions of individual modality components within our model, revealing the significant role of speech content cues. In conclusion, our proposed approach demonstrates considerable potential in predicting turn-taking events within HAI, providing a foundation for future research with physical robots during human-robot interaction (HRI).
  
- **Keywords**: Human-robot interaction; Social cognition; Speech system; Virtual avatar; Language differences; Cross-cultural robotics
  
- **Link**: [Real-Time Multimodal Turn-taking Prediction to Enhance Cooperative Dialogue during Human-Agent Interaction](https://drive.google.com/file/d/1Kh-XhDySf9iaQDU4lKtb9ckFcuWw3C1m/view?usp=drive_link)

## 7. Acknowledgements
This work was supported by a grant from the National Research Foundation of Korea (NRF) (Grant number:2021R1G1A1003801).
