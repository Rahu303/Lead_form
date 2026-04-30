# KeaBuilder AI Assessment — Design and Implementation

This document explains the AI design for KeaBuilder and shows how the prototype implements the requested workflows.

## 1. Lead processing and intelligent response

### a. Classifying leads into hot, warm, cold

Use form fields to compute a score:

- Hot leads:
  - high budget or premium intent
  - short timeline (launch soon)
  - clear conversion goal
  - detailed message
- Warm leads:
  - planning stage
  - moderate timeline
  - some interest but not urgent
- Cold leads:
  - vague goals
  - unclear budget
  - no timeline

Example rule-based scoring in `app.py`:
- `budget` keywords → +2 for strong budget
- `timeline` keywords → +2 for urgent
- `goals` keywords → hot/warm
- long message → +1

### b. Prompts

#### Classification prompt

```text
Classify this lead as hot, warm, or cold based on the provided form inputs. Use urgency, budget, timeline, and expressed goals.

Name: Priya
Email: priya@example.com
Company: GrowthFlow Labs
Budget: We are ready to invest in a premium funnel this quarter.
Timeline: Need to launch within 4 weeks.
Goals: Create a lead capture funnel that converts high-value B2B prospects.
Message: We need a strong offer and automated follow-up sequences.

Return only one of: hot, warm, cold.
```

#### Response generation prompt

```text
You are an assistant for a funnel-building SaaS platform. The lead is classified as hot. Create a human, personalized reply that references the lead's goals and next steps. Use a friendly but professional tone.

Name: Priya
Company: GrowthFlow Labs
Goals: Create a lead capture funnel that converts high-value B2B prospects.
Message: We need a strong offer and automated follow-up sequences.

Suggested reply structure:
1. Thank the lead by name.
2. Mention one key outcome they want.
3. Include a clear next step or offer a call.
4. Keep it warm and human.
```

### c. Ensuring responses feel human and personalized

- Use the lead's name and company in the reply.
- Mention specific goals or details from the message.
- Choose a friendly, conversational tone.
- Add a clear next step, such as "I'll send a proposal" or "Let's schedule a call."
- Avoid robotic phrases like "As an AI model." Keep it supportive and customer-first.

### d. Handling incomplete or unclear inputs

- If fields are missing, use defaults like `N/A` or friendly clarification.
- Ask follow-up questions when the form is not specific.
- Use the available data to still classify loosely.
- In the prototype, the system returns a fallback response when details are missing.

### Sample input → output (JSON)

See `sample_outputs.json`

## 2. Content provider routing design

### System design

KeaBuilder should route content requests by type:

- Images → image provider
- Videos → video provider
- Voice → voice provider

This keeps each provider specialized and reduces complexity.

### Routing logic

- `content_type == "image"` → send to image provider
- `content_type == "video"` → send to video provider
- `content_type == "voice"` → send to voice provider

### Frontend / backend interaction

- Builder UI calls backend endpoint like `/route-content`.
- Backend decides provider and returns the provider payload.
- Frontend shows provider-specific options (style, length, voice, aspect ratio).
- Backend submits the request to the chosen provider.
- Provider response is stored in KeaBuilder asset storage.

### Output management

- Store generated output asset metadata in KeaBuilder (URL, type, status).
- Keep provider details and completion state.
- Show thumbnails/previews in the builder UI.
- Allow users to select an output and place it in funnels or landing pages.

## 3. Personalized AI image generation with LoRA

### Integrating a LoRA model

- Load a pre-trained LoRA adapter for the image model.
- During inference, merge the LoRA weights with the base diffusion model.
- Use prompt conditioning plus personalization tokens.
- Example: `"Apply brand colors from the user’s style and preserve consistent face/brand identity."`

### User workflow in KeaBuilder

1. User selects `Generate Image`.
2. They provide a prompt and optionally upload a brand asset or reference image.
3. Backend selects the base image model and applies the LoRA adapter.
4. Generate images with the user’s brand style and personalization.
5. Store outputs as user assets.

This means each user can get consistent visuals while still using a shared base model.

## 4. Face or text similarity search

### Storage

- Store assets with metadata and vector embeddings.
- For text: store text embeddings.
- For images: store face or visual embeddings.
- Use a vector database or in-memory index for prototypes.

### Retrieval

- Encode query text or image into an embedding.
- Compare against stored embeddings.
- Return top-k matches.

### Matching logic

- Use cosine similarity for text and images.
- For text templates, compare against user input and existing assets.
- For images, use face embeddings or visual feature embeddings.
- Example: if the user uploads a new branding image, find templates with similar colors or style.

## 5. Failover for multiple AI services

### If one model fails

- Detect failure on provider call.
- Retry with a secondary provider.
- Return a graceful message to the user if both fail.
- Keep the UI responsive and avoid showing raw errors.

### If API times out

- Use a timeout threshold for provider calls.
- If timed out, switch to a fallback provider.
- If needed, queue the request and notify the user when complete.

### UX handling

- Show a loading state while waiting.
- If fallback is used, label the output as "Delivered by alternate provider." 
- Keep the experience intact instead of breaking the builder flow.

## 6. High-volume AI request design

### Performance

- Use async request handling.
- Batch similar requests where possible.
- Cache stable outputs and reuse generated assets.

### Cost

- Route cheaper models for drafts and only use premium models for final content.
- Use prompt optimization to reduce token usage.
- Apply provider cost policies by content type.

### Reliability

- Use multiple providers and fallback paths.
- Add health checks and circuit breakers.
- Persist requests and retry failed jobs.
- Separate frontend request handling from backend AI jobs using queues.

## 7. Tools and frameworks

### Example tools used in real projects

- FastAPI / Flask
- Python / Node.js
- OpenAI / Gemini / other LLM APIs
- ElevenLabs for voice
- Stable Diffusion / Runway or Hugging Face for image/video
- PostgreSQL / Redis / vector stores like Pinecone or Weaviate
- GitHub, Docker, AWS/GCP for deployment

## GitHub Profile

Add your GitHub profile link here before submission.

---

### Beginner-friendly explanation

This prototype shows how KeaBuilder can:
- classify leads by urgency and budget,
- generate personalized replies,
- route images/videos/voice to the correct provider,
- use similarity search for assets,
- recover automatically when an AI service fails,
- and scale with multiple providers and async workflows.
