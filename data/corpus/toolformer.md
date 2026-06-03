# Toolformer: Teaching Models to Use Tools

Toolformer is a method for teaching a language model to decide **which** APIs to
call, **when** to call them, **what** arguments to pass, and how to fold the
results back into its generation — all learned in a self-supervised way.

The clever part is how the training data is built. Starting from a plain text
corpus, the model proposes possible API calls at various positions in the text.
Each candidate call is actually executed, and the result is kept only if it
*reduces the model's loss* on predicting the following tokens — that is, only if
the API result genuinely helps explain what comes next. This filtering produces a
new dataset annotated with useful tool calls, and the model is then fine-tuned on
it.

Because the supervision comes from the model's own perplexity rather than human
labels, Toolformer needs only a handful of demonstrations per API. The tools
explored in the original work included a calculator, a question-answering system,
a search engine, a translation system, and a calendar.

The result is a model that learns tool use without sacrificing its core language
abilities, and that calls tools where they actually add value. Toolformer is an
important data point in the argument that tool use can be a *learned* skill baked
into the weights, complementary to prompt-time approaches like ReAct where tool
use is orchestrated at inference time.
