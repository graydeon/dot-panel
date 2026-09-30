// SPDX-License-Identifier: AGPL-3.0-only
import React from 'react';
import {createRoot} from 'react-dom/client';
import Panel from './Panel';
import './styles.css';
createRoot(document.getElementById('root')!).render(<React.StrictMode><Panel/></React.StrictMode>);
