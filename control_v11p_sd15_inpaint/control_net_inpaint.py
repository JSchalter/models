#!/usr/bin/env python3
import torch
import os
from huggingface_hub import HfApi
from pathlib import Path
from diffusers.utils import load_image
from PIL import Image
import numpy as np

from diffusers import (
    ControlNetModel,
    StableDiffusionControlNetPipeline,
    DDIMScheduler,
)
import sys

checkpoint = sys.argv[1]


# pre-process image and mask
image = load_image("https://raw.githubusercontent.com/CompVis/latent-diffusion/main/data/inpainting_examples/overture-creations-5sI6fQgYIuo.png").convert('RGB')
mask_image = load_image("https://raw.githubusercontent.com/CompVis/latent-diffusion/main/data/inpainting_examples/overture-creations-5sI6fQgYIuo_mask.png").convert("L")

# convert to float32
image = np.asarray(image, dtype=np.float32)
mask_image = np.asarray(mask_image, dtype=np.float32)

image[mask_image > 127] = -255.0
image = torch.from_numpy(image)[None].permute(0, 3, 1, 2) / 255.0

prompt = "A blue cat sitting on a park bench"

controlnet = ControlNetModel.from_pretrained(checkpoint, torch_dtype=torch.float16)
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", controlnet=controlnet, torch_dtype=torch.float16
)

pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
pipe.enable_model_cpu_offload()

generator = torch.manual_seed(0)
out_image = pipe(prompt, num_inference_steps=20, generator=generator, image=image, guidance_scale=9.0).images[0]

path = os.path.join(Path.home(), "images", "aa.png")
out_image.save(path)

api = HfApi()

api.upload_file(
    path_or_fileobj=path,
    path_in_repo=path.split("/")[-1],
    repo_id="patrickvonplaten/images",
    repo_type="dataset",
)
print("https://huggingface.co/datasets/patrickvonplaten/images/blob/main/aa.png")
