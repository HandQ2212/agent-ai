"""Exercise the tutorial systems, producing readable real console evidence.
Run from solution/: python3 tutorial/thuc_hanh_tong_hop.py
Uses the trained checkpoint created by train_intent.py and synthetic data.
"""
import asyncio
import json
from pathlib import Path
import torch
from mas_system import Coordinator, single_pipeline
from train_intent import Router, LABELS, dataset, features, metrics

ROOT = Path(__file__).resolve().parents[1]

async def main():
    coordinator = Coordinator(deadline=0.01)
    print('EXERCISE 2 - SHOPPING MAS')
    for query, budget, scenario in [
        ('portable', 100, 'normal'), ('sports', 100, 'normal'),
        ('', 100, 'normal'), ('portable', 100, 'timeout'),
        ('portable', 100, 'malformed'), ('portable', 100, 'stale'),
        ('portable', 100, 'forged'),
    ]:
        response = await coordinator.shop(query, budget, scenario, task_id='demo')
        print('query=%r budget=%s scenario=%s -> %s' %
              (query, budget, scenario, json.dumps(response, ensure_ascii=True)))

    print('\nEXERCISE 3 - TRAINED INTENT CLASSIFIER')
    router = Router(ROOT / 'results/tutorial')
    test = [row for row in dataset() if row['split'] == 'test']
    x = features([row['text'] for row in test], router.vocab)
    with torch.inference_mode():
        probabilities = router.model(x).softmax(1)
    labels = [row['label'] for row in test]
    predicted = probabilities.argmax(1).tolist()
    report = metrics(labels, predicted)
    print('test_count=%d accuracy=%.3f macro_f1=%.3f threshold=%.2f' %
          (len(test), report['accuracy'], report['macro_f1'], router.threshold))
    for i, label in enumerate(LABELS):
        print('%-16s precision=%.3f recall=%.3f' %
              (label, report['precision'][i], report['recall'][i]))
    for text in ['xin ch\u00e0o', 'th\u1eddi ti\u1ebft h\u00f4m nay th\u1ebf n\u00e0o', 'gi\u1ea3i ph\u01b0\u01a1ng tr\u00ecnh']:
        result = router.route(text)
        print('input=%s -> intent=%s confidence=%.3f' %
              (ascii(text), result['intent'], result['confidence']))

    print('\nEXERCISE 5 - BASELINE VS MAS')
    expected = single_pipeline('portable', 100)
    actual = await Coordinator().shop('portable', 100)
    print('single_agent:', json.dumps(expected))
    print('validated_mas:', json.dumps(actual))
    print('same_result:', expected == actual)
    unsafe = await Coordinator(validate=False).shop('portable', 100, 'stale')
    print('without_validation_stale:', json.dumps(unsafe))

if __name__ == '__main__':
    torch.set_num_threads(1)
    asyncio.run(main())
