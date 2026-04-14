export interface MLPlayerMatchStats {
  name: string;
  agent: string;
  predicted_rating: number;
  predicted_acs: number;
  best_role: string;
  worst_role: string;
  flexibility_score: number;
}

export interface MLTeamSummary {
  avg_rating: number;
  avg_acs: number;
  role_distribution: {
    duelist?: number;
    controller?: number;
    initiator?: number;
    sentinel?: number;
  };
}

export interface MLTeamInsights {
  players: MLPlayerMatchStats[];
  summary: MLTeamSummary;
}

export interface MLMatchQueryResponse {
  map: string;
  team_a_win_probability: number;
  team_b_win_probability: number;
  confidence: "High" | "Medium" | "Low";
  model_reasoning: string[];
  team_a: MLTeamInsights;
  team_b: MLTeamInsights;
  insights: string[];
  note: string;
}
