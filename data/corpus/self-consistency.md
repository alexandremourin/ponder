# Self-Consistency

Self-consistency is a decoding strategy that improves chain-of-thought reasoning by
**sampling many reasoning paths and taking a majority vote** over their answers,
instead of greedily decoding a single chain.

The motivation is that complex problems can be solved by more than one valid line
of reasoning, all arriving at the same correct answer, while flawed chains tend to
make different, scattered mistakes. So if you sample a diverse set of chains and
look at where they agree, the correct answer often emerges as the most common
final result — even when any individual chain might be wrong.

The procedure is: prompt the model with chain-of-thought, sample multiple
completions at a non-zero temperature to get diverse reasoning, extract the final
answer from each, and return the answer that appears most frequently. It requires
no extra training and no verifier — just the model and a voting rule.

Self-consistency reliably boosts accuracy on arithmetic and commonsense reasoning
benchmarks over single-path CoT. The trade-off is cost: generating and aggregating
many samples multiplies inference compute, and the gains eventually plateau as the
number of samples grows.

It is most applicable when answers are discrete and easy to compare (a number, a
label, a short span) so that votes can be tallied. The broader principle — that
aggregating multiple independent attempts beats trusting one — connects
self-consistency to ensemble methods and to RAG-Fusion, which fuses results from
multiple query variations.
