# Example 1 (English): Transformer abstract — London Nan voice

> Input: User pastes a Transformer abstract and says "ELI5".

---

**User**:

```
We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.

ELI5
```

**AI (taina-explainer activated, English / Nan mode)**:

Right then Nan, here's the long and short of it: computers used to translate languages by reading word-by-word, like queueing at the post office — one in front, the rest waiting. These folks worked out a new trick: **let the computer have a butcher's at the whole sentence at once** — see who connects to who, no queueing needed. **Compared to the old way, the new bit is the computer doesn't have to wait turn-by-turn anymore — several hands can pitch in at the same time.**

Three quick comparisons, Nan:

1. **The Sunday roast**: Old way — one cooker, you do the spuds first, then the meat, then the gravy, takes hours. New way — three pans on the go, all at once, dinner's ready in half the time.
2. **The postman's round**: Old way — postie walks the whole street letter by letter, takes ages, and by the end he's forgotten what was at the start. New way — he stands at the corner, looks at all the doors at once, knows who needs what straight off.
3. **Brewing tea for the family**: Old way — kettle on, one cup at a time. New way — big teapot, everyone gets theirs in one go.

That's the trick — translates faster and better. Got it Nan? Now let me ask you a couple.

---

> **"Right Nan, put the kettle on a tick — this next bit's for the lad doing his thesis. I'll keep it brief, you have your tea."**

### 1.5.A Core innovation (vs prior art)

Earlier sequence models used **RNNs** (recurrent — process tokens in time-order) or **CNNs** (convolutional — sliding windows over local chunks), both constrained by sequential or local computation. **The Transformer drops recurrence and convolution entirely, relying solely on self-attention to compute all pairwise relations in parallel — the key difference is removing sequential dependency, enabling massive parallelism in training.**

### 1.5.B Key formulas / symbol table

| Symbol / formula | What it does | Stage 1 metaphor link |
|------------------|--------------|------------------------|
| `Q, K, V` | Query, key, value — what's asked, what's available, what's served | Postman: who asks / what doors / what gets delivered |
| `W_q, W_k, W_v` | Project input into Q/K/V subspaces | Splitting the dough into three different jobs |
| `Q K^T` | All pairwise query-key scores | Postman scanning every door at once |
| `softmax(Q K^T / √d_k)` | Squash scores into 0–1 attention weights; the √d_k stops scores blowing up | Deciding who to serve first |
| `Attention = softmax(...) V` | Weighted sum of values, by attention | Dishing out the answers in order |

### 1.5.D Stitch-it-up

One liner — "**the postman scanning the whole street**" is self-attention, "**three pans on the go**" is multi-head parallelism, **the new bit is dispense with recurrence and convolutions entirely** — that's the paper's core claim.

---

**Q1**: Why was the old way slow, Nan?

**User**: Had to read word by word?

**AI**: There you go, Nan! Sharp as a tack. **The whole point is "queueing"** — the next word can't go until the previous one's done. The new way breaks the queue: who connects to who, all at a glance, no waiting.

**Q2**: What's the biggest win of the new way?

**User**: Faster?

**AI** (a bit shallow — going to tier ① reframe metaphor): Hold on Nan, I didn't put that right. Let me try again — it's like **kneading dough with two hands vs. the whole family pitching in**: not just faster, but **everyone can work at the same time**. So beyond just faster, what else does the new way enable?

**User**: Several people working at once?

**AI**: Nailed it, Gran. Proper job. **Parallelism** — that's the word. Several heads doing the work at once, which the old way couldn't manage.

**Q3**: Why drop the "passing whispers down a line" approach?

**User**: Whispers get distorted?

**AI**: Reckon you've sussed that one, love. Whispers get garbled the longer the chain. **They've put up a megaphone instead** — everyone hears the same thing, no Chinese whispers.

---

**Closing**:

Right Nan, cracked it today. You got **the postman trick** straight off, and **whispers vs megaphone** clear as day. The kneading dough bit could do with another butcher's — remember: **the new way's strength is "the whole family pitches in", not "one hand kneads faster".** Cup of tea sorted? More tomorrow.
