import React, { useEffect, useState } from 'react';
import { ProjectWorkspace } from '../workspace/project-workspace';
import { GovernanceView } from './GovernanceView';

const App: React.FC = () => {
  const [path, setPath] = useState(window.location.pathname);

  useEffect(() => {
    const handleLocationChange = () => {
      setPath(window.location.pathname);
    };
    window.addEventListener('popstate', handleLocationChange);
    return () => window.removeEventListener('popstate', handleLocationChange);
  }, []);

  if (path.startsWith('/governance')) {
    return <GovernanceView />;
  }

  return <ProjectWorkspace />;
};

export default App;
