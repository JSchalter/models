#!/usr/bin/env python3
import torch
import os
from huggingface_hub import HfApi
from pathlib import Path
from diffusers.utils import load_image
from controlnet_aux import LineartDetector

from diffusers import (
    ControlNetModel,
    StableDiffusionControlNetPipeline,
    UniPCMultistepScheduler,
)
import sys

checkpoint = sys.argv[1]

url = "https://github.com/lllyasviel/ControlNet-v1-1-nightly/raw/main/test_imgs/bag.png"
url = "https://github.com/lllyasviel/ControlNet-v1-1-nightly/raw/main/test_imgs/person_1.jpeg"
image = load_image(url)

prompt = "michael jackson concert"

processor = LineartDetector.from_pretrained("lllyasviel/Annotators")
image = processor(image)
image.save("/home/patrick/images/check.png")

controlnet = ControlNetModel.from_pretrained(checkpoint, torch_dtype=torch.float16)
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", controlnet=controlnet, torch_dtype=torch.float16
)

pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_model_cpu_offload()

generator = torch.manual_seed(0)
out_image = pipe(prompt, num_inference_steps=30, generator=generator, image=image).images[0]

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
