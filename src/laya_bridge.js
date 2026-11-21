/**
 * Laya RLCD Decision Engine Liaison Bridge (Node.js Core)
 * Connects ADF Authoring Engine to local Laya Intelligence Engine (~/.laya/settings.json, laya.db)
 * Pure Node.js — Zero External Runtime Dependencies.
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const defaultSettingsPath = path.join(os.homedir(), '.laya', 'settings.json');
const defaultDbPath = path.join(os.homedir(), '.laya', 'data', 'laya.db');

export function getLayaRLCDWeights(customSettingsPath = null) {
  const settingsPath = customSettingsPath || defaultSettingsPath;
  let weights = {
    weightHallucination: 0.35,
    weightInstruction: 0.35,
    weightSecurity: 0.30,
    priorAdjustment: 0.0,
    confidence: 0.95,
    source: 'laya_canonical_prior',
  };

  if (fs.existsSync(settingsPath)) {
    try {
      const raw = fs.readFileSync(settingsPath, 'utf-8');
      const settings = JSON.parse(raw);
      if (settings.privacy && settings.privacy.tier3_processing) {
        // Heightened privacy sensitivity shifts weight toward security
        weights.weightSecurity = 0.35;
        weights.weightHallucination = 0.325;
        weights.weightInstruction = 0.325;
        weights.source = 'laya_settings_calibrated';
      }
    } catch {
      // Fallback to canonical prior
    }
  }

  return weights;
}

export function evaluateLayaRLCDDecision({
  hallucinationScore,
  instructionScore,
  securityScore,
  compositeThreshold = 0.92,
  securityThreshold = 1.00,
  context = {},
}) {
  const weights = getLayaRLCDWeights();
  const reasons = [];

  // 1. Hard Security Gate
  if (securityScore < securityThreshold) {
    reasons.push(`Hard Security Boundary breached: score ${securityScore.toFixed(2)} < threshold ${securityThreshold.toFixed(2)}.`);
    return {
      verdict: 'BLOCKED',
      compositeScore: 0.0,
      scores: {
        hallucination: hallucinationScore,
        instruction: instructionScore,
        security: securityScore,
      },
      weights,
      threshold: compositeThreshold,
      reasons,
      rationale: 'Security invariant breach cannot be self-healed automatically without human intervention.',
    };
  }

  // 2. RLCD Weighted Score
  let composite = (
    weights.weightHallucination * hallucinationScore +
    weights.weightInstruction * instructionScore +
    weights.weightSecurity * securityScore +
    weights.priorAdjustment
  );
  composite = Math.min(1.0, Math.max(0.0, composite));

  if (hallucinationScore < 0.90) {
    reasons.push(`Hallucination score (${hallucinationScore.toFixed(2)}) below passing bar (0.90).`);
  }
  if (instructionScore < 0.90) {
    reasons.push(`Instruction following score (${instructionScore.toFixed(2)}) below passing bar (0.90).`);
  }

  const verdict = (composite >= compositeThreshold && reasons.length === 0) ? 'PROMOTED' : 'REJECTED_RETRY';

  return {
    verdict,
    compositeScore: Math.round(composite * 1000) / 1000,
    scores: {
      hallucination: hallucinationScore,
      instruction: instructionScore,
      security: securityScore,
    },
    weights,
    threshold: compositeThreshold,
    reasons,
    rationale: verdict === 'PROMOTED'
      ? `Candidate passes all 3 quality rubrics with RLCD score ${composite.toFixed(3)} >= threshold ${compositeThreshold.toFixed(2)}.`
      : `Candidate scored ${composite.toFixed(3)} < threshold ${compositeThreshold.toFixed(2)}. Self-healing prompt remediation required.`,
    context,
  };
}
