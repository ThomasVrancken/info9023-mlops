from vllm import LLM, SamplingParams

# Set up our model 
llm = LLM(
    model="facebook/opt-125m", 
    device="cpu",           
    dtype="float16"        
)

# Configure generation parameters
sampling_params = SamplingParams(
    temperature=0.8,    # Controls randomness
    top_p=0.95,        # Controls diversity
    max_tokens=100     # Controls length of the generated text
)

# Let's test it out!
prompts = ["vLLM is an open-source powerful because"]
outputs = llm.generate(prompts, sampling_params)

# See what we got
for output in outputs:
    print(f"Prompt: {output.prompt}")
    print(f"Generated: {output.outputs[0].text}")
    