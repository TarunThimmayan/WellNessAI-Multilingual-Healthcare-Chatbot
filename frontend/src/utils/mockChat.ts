import type { Message } from '../components/ChatMessage';

const sampleResponses: string[] = [
  `### Here's what I found

- Drink **plenty of water** to stay hydrated.
- Keep a simple diary of when the symptoms appear.
- Watch for warning signs like persistent chest pain or shortness of breath.

> If symptoms worsen, contact your doctor or local emergency services.`,
  `### Self-care checklist

1. Rest with your head slightly elevated.
2. Use a humidifier to keep the air moist.
3. Try gentle breathing exercises twice a day.

[Learn breathing exercises](https://www.nhs.uk/live-well/exercise/)`,
  `### When to seek urgent care

- Sudden weakness on one side of the body.
- New or severe headache with visual changes.
- Fainting or chest pain that spreads to the arm/jaw.

If you notice these, call your local emergency number.`,
];

function pickRandom<T>(items: T[]): T {
  return items[Math.floor(Math.random() * items.length)];
}

export async function sendMockMessage(input: string): Promise<Omit<Message, 'id'>> {
  return new Promise((resolve, reject) => {
    const latency = Math.random() * 1200 + 700;
    const shouldError = input.toLowerCase().includes('error');

    setTimeout(() => {
      if (shouldError) {
        reject(
          new Error(
            'Unable to connect to the health assistant right now. Please try again shortly.'
          )
        );
        return;
      }

      resolve({
        role: 'assistant',
        content: pickRandom(sampleResponses),
        timestamp: new Date().toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        }),
      });
    }, latency);
  });
}

