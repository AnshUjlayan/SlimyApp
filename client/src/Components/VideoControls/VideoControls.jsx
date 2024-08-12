import React from "react";
import styles from "./VideoControls.module.css";
import Description from "./Description";
import {
  FaThumbsUp,
  FaThumbsDown,
  FaAngleRight,
  FaAngleLeft,
} from "react-icons/fa";
import { useNavigate } from "react-router-dom";

const VideoControls = (props) => {
  const navigate = useNavigate();

  const handleNextClick = () => {
    const nextIndex = parseInt(props.currVideoIdx) + 1;
    if (nextIndex < props.bundleSize) {
      props.updateIdx(nextIndex);
    }
  };

  const handleBackClick = () => {
    const nextIndex = props.currVideoIdx - 1;
    if (nextIndex >= 0) {
      props.updateIdx(nextIndex);
    }
  };

  return (
    <>
      <h1 className={styles["videoTopic"]}>{props.title}</h1>
      <div className={styles["video-controls"]}>
        <div
          onClick={() => navigate(`/u/${props.authorUsername}`)}
          className={styles.flex}
        >
          <div className={styles.author}>
            <img src={props.authorProfile} alt="Author Profile" />
            <h1>{props.authorName}</h1>
          </div>
        </div>

        <div className={styles.flex}>
          <div className={styles.likesDislikes}>
            <div
              onClick={props.updateLiked}
              className={`${styles["btn-hover"]} ${styles["color-5-back"]} ${
                styles["btn-hover-back"]
              } ${props.isLiked && styles.selected}`}
            >
              <FaThumbsUp className={styles.icon} />
              <p>{props.likes}</p>
            </div>
            <div
              onClick={props.updateDisliked}
              className={`${styles["btn-hover"]} ${styles["color-5"]} ${
                styles["btn-hover"]
              }  ${props.isDisliked && styles.selected}`}
            >
              <FaThumbsDown className={styles.icon} />
              <p>{props.dislikes}</p>
            </div>
          </div>

          <div className={styles.buttons}>
            <button
              className={`${styles["btn-hover"]} ${styles["color-5-back"]} ${styles["btn-hover-back"]}`}
              onClick={handleBackClick}
            >
              <div className={styles.nextFlex}>
                <FaAngleLeft className={styles.icon} />
                Back
              </div>
            </button>
          </div>
          <div className={styles.buttons}>
            <button
              className={`${styles["btn-hover"]} ${styles["color-5"]}`}
              onClick={handleNextClick}
            >
              <div className={styles.nextFlex}>
                Next
                <FaAngleRight className={styles.icon} />
              </div>
            </button>
          </div>
        </div>
      </div>
      <Description desc={props.desc} />
    </>
  );
};

export default VideoControls;
