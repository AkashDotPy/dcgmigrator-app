import { useEffect, useState } from "react";
import axios from "axios";

const ApiManager = (URL) => {
  const [data, setData] = useState([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(false);

        const response = await axios.get(URL);
        setData(response.data);

        setLoading(false);
      } catch (error) {
        setError(true);
        setLoading(false);
      }
    };

    fetchData();
  }, [URL]);

  return [data, error, loading];
};

export default ApiManager;