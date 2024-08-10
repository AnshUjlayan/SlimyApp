import React, { useEffect, useState } from "react";
import styles from "./Home.module.css";
import HomeFeed from "../../Components/HomeFeed/HomeFeed";
import Gemini from "../../Components/Gemini/Gemini";
import HomeSkeleton from "../../Components/Skeleton/HomeSkeleton";
import api from "../../Config/apiConfig.js";
import useAlerts from "../../Hooks/useAlerts";

const Home = () => {
  const { addAlert } = useAlerts();
  const [loading, setLoading] = useState(true);
  const [recommendedPlaylistData, setRecommendedPlaylistData] = useState([]);
  const [popularPlaylistData, setPopularPlaylistData] = useState([]);
  const [recentUploadsPlaylistData, setRecentUploadsPlaylistData] = useState(
    [],
  );

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);

      const fetchRecommendedPlaylistData = api
        .get("playlist/recommended")
        .then((response) => {
          setRecommendedPlaylistData(response.data);
        })
        .catch((error) => {
          console.error("Error fetching recommended playlists:", error);
          addAlert("Error", "Error fetching recommended playlists");
        });

      const fetchPopularPlaylistData = api
        .get("playlist/popular")
        .then((response) => {
          setPopularPlaylistData(response.data);
        })
        .catch((error) => {
          console.error("Error fetching popular playlists:", error);
          addAlert("Error", "Error fetching popular playlists");
        });

      const fetchRecentUploadsPlaylistData = api
        .get("playlist/recent-uploads")
        .then((response) => {
          setRecentUploadsPlaylistData(response.data);
        })
        .catch((error) => {
          console.error("Error fetching recent uploads:", error);
          addAlert("Error", "Error fetching recent uploads");
        });

      await Promise.all([
        fetchRecommendedPlaylistData,
        fetchPopularPlaylistData,
        fetchRecentUploadsPlaylistData,
      ]);

      setLoading(false);
    };

    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) {
    return (
      <div className={styles.container}>
        <Gemini />
        <HomeSkeleton />
      </div>
    );
  }

  const feedList = [
    {
      id: 1,
      category: "Recommended",
      data: recommendedPlaylistData,
    },
    {
      id: 2,
      category: "Popular",
      data: popularPlaylistData,
    },
    {
      id: 3,
      category: "Recently Uploaded",
      data: recentUploadsPlaylistData,
    },
  ];

  return (
    <div className={styles.container}>
      <Gemini />
      <HomeFeed feedList={feedList} />
    </div>
  );
};

export default Home;
