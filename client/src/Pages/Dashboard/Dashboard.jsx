import React, { useState, useEffect } from "react";
import styles from "./Dashboard.module.css";
import ProfileHeader from "../../Components/ProfileHeader/ProfileHeader";
import Analytics from "../../Components/Analytics/Analytics";
import HomeFeed from "../../Components/HomeFeed/HomeFeed";
import DashboardSkeleton from "../../Components/Skeleton/DashboardSkeleton";
import ActivityCalendar from "../../Components/ActivityCalendar/ActivityCalendar.jsx";
import api from "../../Config/apiConfig.js";
import { useParams } from "react-router-dom";

const Dashboard = () => {
  const { username } = useParams();
  const user = localStorage.getItem("user")
    ? JSON.parse(localStorage.getItem("user"))
    : null;

  const [createdPlaylists, setCreatedPlaylists] = useState([]);
  const [likedPlaylists, setLikedPlaylists] = useState([]);
  const [createdDrafts, setCreatedDrafts] = useState([]);
  const [bookmarkedPlaylists, setBookmarkedPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCreatedPlaylists = api.get(`playlist/user-playlists`, {
      params: { username },
    });
    const fetchLikedPlaylists = api.get(`playlist/user-liked-playlists`, {
      params: { username },
    });

    let fetchCreatedDrafts;
    let fetchBookmarkedPlaylists;

    if (user && username === user.username) {
      fetchCreatedDrafts = api.get(`draft/get-all-drafts`, {
        params: { username },
      });
      fetchBookmarkedPlaylists = api.get(`playlist/user-bookmarked-playlists`);
    }

    const requests = [
      fetchCreatedPlaylists,
      fetchLikedPlaylists,
      fetchCreatedDrafts,
      fetchBookmarkedPlaylists,
    ].filter(Boolean);

    Promise.all(requests)
      .then((responses) => {
        const [
          createdPlaylistsResponse,
          likedPlaylistsResponse,
          createdDraftsResponse,
          bookmarkedPlaylistsResponse,
        ] = responses;
        setCreatedPlaylists(createdPlaylistsResponse.data);
        setLikedPlaylists(likedPlaylistsResponse.data);
        if (createdDraftsResponse) {
          setCreatedDrafts(createdDraftsResponse.data);
        }
        if (bookmarkedPlaylistsResponse) {
          setBookmarkedPlaylists(bookmarkedPlaylistsResponse.data);
        }
      })
      .catch((error) => {
        console.error("Error fetching playlist data: ", error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [username]);

  if (loading) {
    return <DashboardSkeleton />;
  }

  const analyticsData = {
    views: 0,
    likes: 0,
    dislikes: 0,
  };

  const activityData = createdPlaylists.map((playlist) => {
    analyticsData.views += playlist.views;
    analyticsData.likes += playlist.likes;
    analyticsData.dislikes += playlist.dislikes;

    return {
      date: playlist.created_at,
    };
  });

  const feedList = [
    {
      id: 1,
      category: "Playlists",
      data: createdPlaylists,
    },
    {
      id: 2,
      category: "Liked",
      data: likedPlaylists,
    },
    {
      id: 3,
      category: "Bookmarks",
      data: bookmarkedPlaylists,
    },
    {
      id: 4,
      category: "Drafts",
      data: createdDrafts,
      isDraft: true,
    },
  ];

  if (!user || username !== user.username) {
    feedList.splice(2, 2);
  }

  return (
    <>
      <div className={styles.top}>
        <div className={styles.profileHeader}>
          <ProfileHeader />
        </div>
        <div className={styles.analytics}>
          <Analytics analyticsData={analyticsData} />
        </div>
      </div>
      {/* <ActivityCalendar analyticsData={activityData} /> */}
      <HomeFeed feedList={feedList} />
    </>
  );
};

export default Dashboard;
