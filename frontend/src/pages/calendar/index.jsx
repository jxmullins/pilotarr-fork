import React, { useState, useEffect } from "react";
import Header from "../../components/navigation/Header";
import Icon from "../../components/AppIcon";

import CalendarGrid from "./components/CalendarGrid";
import EventSidebar from "./components/EventSidebar";
import ViewToolbar from "./components/ViewToolbar";
import { getCalendarEvents } from "../../services/calendarService";

const Calendar = () => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [viewMode, setViewMode] = useState("month");
  const [eventFilters, setEventFilters] = useState({
    tvReleases: true,
    movieReleases: true,
  });
  const [events, setEvents] = useState([]);
  const [selectedDateEvents, setSelectedDateEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch events whenever the displayed month changes
  useEffect(() => {
    const year = selectedDate.getFullYear();
    const month = selectedDate.getMonth();
    const start = `${year}-${String(month + 1).padStart(2, "0")}-01`;
    const lastDay = new Date(year, month + 1, 0).getDate();
    const end = `${year}-${String(month + 1).padStart(2, "0")}-${String(lastDay).padStart(2, "0")}`;

    setIsLoading(true);
    getCalendarEvents(start, end).then((data) => {
      setEvents(data);
      setIsLoading(false);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDate.getFullYear() * 100 + selectedDate.getMonth()]);

  // Update selected date events when date or filters change
  useEffect(() => {
    const filteredEvents = getEventsForDate(selectedDate);
    setSelectedDateEvents(filteredEvents);
  }, [selectedDate, events, eventFilters]);

  const getEventsForDate = (date) => {
    return events?.filter((event) => {
      const eventDate = new Date(event?.releaseDate);
      const matchesDate =
        eventDate?.getDate() === date?.getDate() &&
        eventDate?.getMonth() === date?.getMonth() &&
        eventDate?.getFullYear() === date?.getFullYear();

      if (!matchesDate) return false;

      // Apply event type filters
      if (
        event?.eventType === "release" &&
        event?.type === "tv" &&
        !eventFilters?.tvReleases
      )
        return false;
      if (
        event?.eventType === "release" &&
        event?.type === "movie" &&
        !eventFilters?.movieReleases
      )
        return false;

      return true;
    });
  };

  const navigateMonth = (direction) => {
    const newDate = new Date(selectedDate);
    newDate?.setMonth(newDate?.getMonth() + direction);
    setSelectedDate(newDate);
  };

  const goToToday = () => {
    setSelectedDate(new Date());
  };

  const monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 pt-20 md:pt-24 pb-6 md:pb-8">
        {/* Page Header */}
        <div className="mb-6 md:mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Icon name="Calendar" size={20} color="var(--color-primary)" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-foreground">
                Media Calendar
              </h1>
              <p className="text-sm text-muted-foreground">
                Track TV show and movie releases from Sonarr and Radarr
              </p>
            </div>
          </div>
        </div>

        {/* View Toolbar */}
        <ViewToolbar
          viewMode={viewMode}
          setViewMode={setViewMode}
          eventFilters={eventFilters}
          setEventFilters={setEventFilters}
          selectedDate={selectedDate}
          monthNames={monthNames}
          navigateMonth={navigateMonth}
          goToToday={goToToday}
        />

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Calendar Grid */}
          <div className="lg:col-span-2">
            <CalendarGrid
              selectedDate={selectedDate}
              setSelectedDate={setSelectedDate}
              events={events}
              eventFilters={eventFilters}
              viewMode={viewMode}
              isLoading={isLoading}
            />
          </div>

          {/* Event Sidebar */}
          <div className="lg:col-span-1">
            <EventSidebar
              selectedDate={selectedDate}
              events={selectedDateEvents}
              isLoading={isLoading}
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Calendar;
