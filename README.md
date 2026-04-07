# digby-oldridge-heritage-physics
Spectrophotometric tools and master taxonomy for the Digby Oldridge Heritage Archive (v44).
# Digby Oldridge Heritage Physics Library (v44)

[![Hugging Face Dataset](https://img.shields.io/badge/%F0%9F%A4%97-Dataset-yellow)](https://huggingface.co/datasets/DigbyOldridge/digby-oldridge-heritage-archive)
[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)

This repository contains the technical engine and master taxonomy for the **Digby Oldridge Heritage Colour Archive**. While our high-density AI training sets (SFT/DPO) are hosted on Hugging Face, this library provides the Python tools for **Chromatic Validation** and **RAG (Retrieval-Augmented Generation)**.

## 🏺 The Digital-to-Physical Standard
This archive underpins the **[digby.shop](https://digby.shop)** product line. Every CIELAB coordinate in this dataset corresponds to a physical pigment batch in our Oxfordshire archive, providing a 99.8% spectrophotometric match between digital design and physical application.

## 🛠️ Included Tools

### 1. Digby RAG Demo (`digby_rag_demo.py`)
Demonstrates how to perform exact colourimetric lookups using CIELAB ΔE76 distance. 
* **Search by Name:** `python3 digby_rag_demo.py --name "Wayland Void Blue"`
* **Search by Hex:** `python3 digby_rag_demo.py --hex "#141820"`

### 2. Chromatic Lock Validator (`chromatic_lock_validator_v44.py`)
The verification engine that ensures any model trained on this archive maintains 100% fidelity to the original spectrophotometric measurements.

## 🌍 Climate-Aware Specification
Unlike generic colour libraries, this archive includes **Material Science Guardrails**:
* **Tropical Red-Teaming:** Logic to prevent binder failure and thermal delamination in high-UV zones.
* **Freeze-Thaw Logic:** Sub-zero substrate guidance for Highland and northern climates.

## 🚀 Quick Start
```bash
git clone [https://github.com/DigbyOldridge/digby-oldridge-heritage-physics.git](https://github.com/DigbyOldridge/digby-oldridge-heritage-physics.git)
cd digby-oldridge-heritage-physics
pip install numpy
python3 digby_rag_demo.py --demo
