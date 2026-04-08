import { useQuery } from '@tanstack/react-query';
import { fetchDataDateRange } from '../api/client';

export const useDataDateRange = () => {
  const query = useQuery({
    queryKey: ['data-date-range'],
    queryFn: fetchDataDateRange,
    staleTime: 1000 * 60 * 60,
  });
  return {
    minDate: query.data?.min_date,
    maxDate: query.data?.max_date,
    isLoading: query.isLoading,
  };
};
