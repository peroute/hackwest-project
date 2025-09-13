import React from 'react';
import styles from '../styles/LoadingSpinner.module.css';

// LoadingSpinner: Simple animated spinner for loading states
// Props: { size?: number }
const LoadingSpinner = ({ size = 20 }) => (
  <span
    className={styles.spinner}
    style={{ width: size, height: size }}
    aria-label="Loading"
    role="status"
  />
);

export default LoadingSpinner;
