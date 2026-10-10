// Temperature conversion and display formatting utilities
export function convertTemp(tempC, unit = '°C') {
  if (typeof tempC !== 'number' || Number.isNaN(tempC)) return tempC
  if (unit === '°F') {
    return Math.round((tempC * 1.8 + 32) * 10) / 10
  }
  return Math.round(tempC * 10) / 10
}

export function formatTemp(tempC, unit = '°C') {
  if (typeof tempC !== 'number' || Number.isNaN(tempC)) return tempC
  return `${convertTemp(tempC, unit)}${unit}`
}
