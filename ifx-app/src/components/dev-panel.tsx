'use client';

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";

export default function DevPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const { toast } = useToast();

  return (
    <div>
      <Button onClick={() => setIsOpen(!isOpen)} className="absolute bottom-4 right-4">
        {isOpen ? 'Hide' : 'Show'} Dev Panel
      </Button>
      {isOpen && (
        <div className="absolute bottom-16 right-4 bg-white dark:bg-gray-800 p-4 rounded-lg shadow-lg w-96">
          <h3 className="font-bold mb-4">Settings</h3>
          <div className="space-y-4">
            <div>
              <Label htmlFor="zep">Zep</Label>
              <Input id="zep" placeholder="Zep URL" />
            </div>
            <div>
              <Label htmlFor="freeplay">Freeplay</Label>
              <Input id="freeplay" placeholder="Freeplay API Key" />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="Email" />
            </div>
            <div>
              <Label htmlFor="first-name">First Name</Label>
              <Input id="first-name" placeholder="First Name" />
            </div>
            <div>
              <Label htmlFor="last-name">Last Name</Label>
              <Input id="last-name" placeholder="Last Name" />
            </div>
            <Button
              onClick={() => {
                toast({
                  title: "Scheduled: Catch up",
                  description: "Friday, February 10, 2023 at 5:57 PM",
                });
              }}
            >
              Show Toast
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
