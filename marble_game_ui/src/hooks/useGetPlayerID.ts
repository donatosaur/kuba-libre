import { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

// set the key whose value is the playerID
const key = "http://database_id"

export function useGetPlayerID() {
    const [playerID, setPlayerID] = useState<string | null>(null);
    const { isAuthenticated, getIdTokenClaims } = useAuth0();

    useEffect(() => {
        void async function getPlayerID() {
            if (!isAuthenticated) {
                return;
            }
            const claims = await getIdTokenClaims();
            if (!Boolean(claims[key])) {
                console.log(`Error: missing claims key=${key}`);
                return;
            }

            setPlayerID(claims[key]);
        }();
    }, [isAuthenticated]);

    return { playerID, setPlayerID };
}
