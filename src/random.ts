export function float(min=0, max=1): number {
  return min + (max - min) * Math.random()
}

export function int(min=0, max=Number.MAX_SAFE_INTEGER): number {
  return Math.floor(min + (max - min) * Math.random())
}

export function id(length=16): string {
  return Array.from({length: length}, _ => int(0, 36))
    .map(x => x < 10 ? x + "0".charCodeAt(0) : x - 10 + "a".charCodeAt(0))
    .map(x => String.fromCharCode(x))
    .join()
}
