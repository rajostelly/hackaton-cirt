import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/api/client";
import type { AlertOut, Criticity } from "@/api/types";

// https://tanstack.com/query/v5/docs/framework/react/guides/queries
export function useOpenAlerts(criticity?: Criticity) {
  return useQuery<AlertOut[]>({
    queryKey: ["alerts", "open", criticity ?? null],
    queryFn: async () => {
      const params: Record<string, unknown> = { limit: 100 };
      if (criticity) params.criticity = criticity;
      const { data } = await apiClient.get<AlertOut[]>("/alerts", { params });
      return data;
    },
    refetchInterval: 5_000,
  });
}

export function useAlert(id: string) {
  return useQuery<AlertOut>({
    queryKey: ["alerts", id],
    queryFn: async () => {
      const { data } = await apiClient.get<AlertOut>(`/alerts/${id}`);
      return data;
    },
  });
}

// https://tanstack.com/query/v5/docs/framework/react/guides/mutations
export function useTriageAlert() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      isFalsePositive,
    }: {
      id: string;
      isFalsePositive: boolean;
    }) => {
      const { data } = await apiClient.post<AlertOut>(
        `/alerts/${id}/triage`,
        { is_false_positive: isFalsePositive },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
}
