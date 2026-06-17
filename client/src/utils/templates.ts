import type { TemplateDef } from '../types/template'
import { loadCustomTemplates } from './customTemplates'

import classicDef from '../templates/classic.json'
import modernDef from '../templates/modern.json'
import minimalDef from '../templates/minimal.json'

const builtIn: Record<string, TemplateDef> = {
  classic: classicDef as TemplateDef,
  modern: modernDef as TemplateDef,
  minimal: minimalDef as TemplateDef,
}

function allDefs(): Record<string, TemplateDef> {
  const merged = { ...builtIn }
  for (const t of loadCustomTemplates()) {
    merged[t.id] = t
  }
  return merged
}

export function getTemplateDef(id: string): TemplateDef {
  return allDefs()[id] ?? builtIn.classic
}

export function getAllTemplateDefs(): TemplateDef[] {
  return Object.values(allDefs())
}

export function getBuiltinDefs(): Record<string, TemplateDef> {
  return { ...builtIn }
}
