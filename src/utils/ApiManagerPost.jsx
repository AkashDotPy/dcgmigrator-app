import React, { useEffect, useState } from "react";
import axios from "axios";

const ApiManagerPost = (URL, requestData) => {
  const [data, setData] = useState([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(false);

        const response = await axios.post(URL,requestData);
        setData(response.data);
        setLoading(false);

      } catch (error) {
        setError(true);
        setLoading(false);
      }
    };

    fetchData();
  }, [URL, requestData]);

  return [data, error, loading];
};

export default ApiManagerPost;