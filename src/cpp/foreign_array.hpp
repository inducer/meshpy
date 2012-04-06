#ifndef _HEADER_SEEN_FOREIGN_ARRAY
#define _HEADER_SEEN_FOREIGN_ARRAY




#include <vector>
#include <stdexcept>
#include <boost/python.hpp>




class tSizeChangeNotifier;




class tSizeChangeNotificationReceiver
{
  public:
    virtual ~tSizeChangeNotificationReceiver()
    { }
    virtual void notifySizeChange(tSizeChangeNotifier *master, unsigned size) = 0;
};




class tSizeChangeNotifier
{
    typedef std::vector<tSizeChangeNotificationReceiver *> tNotificationReceiverList;
    tNotificationReceiverList NotificationReceivers;

  public:
    virtual ~tSizeChangeNotifier()
    { }
    virtual unsigned size() const = 0;
    virtual void setSize(unsigned size)
    {
      tNotificationReceiverList::iterator first = NotificationReceivers.begin(),
      last = NotificationReceivers.end();
      while (first != last)
	(*first++)->notifySizeChange(this, size);
    }

    void registerForNotification(tSizeChangeNotificationReceiver *rec)
    {
      NotificationReceivers.push_back(rec);
    }

    void unregisterForNotification(tSizeChangeNotificationReceiver *rec)
    {
      tNotificationReceiverList::iterator first = NotificationReceivers.begin(),
      last = NotificationReceivers.end();
      while (first != last)
      {
	if (rec == *first)
	{
	  NotificationReceivers.erase(first);
	  return;
	}
	first++;
      }
    }
};




template<class ElementT> 
class tReadOnlyForeignArray : public tSizeChangeNotifier, public tSizeChangeNotificationReceiver,
  public boost::noncopyable
{
  protected:
    ElementT	                *&Contents;
    int		                &NumberOf;
    unsigned	                Unit;
    tSizeChangeNotifier         *SlaveTo;
    bool                        AssumeOwnership;

  public:
    typedef ElementT value_type;

    tReadOnlyForeignArray(
        ElementT *&cts, int &number_of, unsigned unit=1, tSizeChangeNotifier *slave_to=NULL,
        bool assume_ownership=false)
      : Contents(cts), NumberOf(number_of), Unit(unit), SlaveTo(slave_to), 
      AssumeOwnership(assume_ownership)
    {
      if (AssumeOwnership)
        Contents = NULL;

      if (SlaveTo)
      {
	SlaveTo->registerForNotification(this);
	setSizeInternal(SlaveTo->size());
      }
      else
      {
        if (AssumeOwnership)
          setSize(0);
      }
    }

    ~tReadOnlyForeignArray()
    {
      if (SlaveTo)
	SlaveTo->unregisterForNotification(this);

      if (AssumeOwnership)
      {
        deallocate();

        if (!SlaveTo)
          NumberOf = 0;
      }
    }

    unsigned size() const
    {
      return NumberOf;
    }

    unsigned unit() const
    {
      return Unit;
    }

    bool is_allocated()
    {
      return Contents != NULL;
    }

    void deallocate()
    {
      if (Contents != NULL)
	delete[] Contents;
      Contents = NULL;
    }

    void setSize(unsigned size)
    {
      if (SlaveTo)
	throw std::runtime_error("sizes of slave arrays cannot be changed");
      else
	setSizeInternal(size);
    }
    
    void setup()
    {
      if (!SlaveTo)
	throw std::runtime_error("cannot setup non-slave array");
      else
      {
        if (!Contents)
          setSizeInternal(NumberOf);
      }
    }

    void notifySizeChange(tSizeChangeNotifier *master, unsigned size)
    {
      if (!SlaveTo)
	throw std::runtime_error("non-slave array should not get size notifications");

      // only perform size change if we actually existed
      if (Contents)
        setSizeInternal(size);
    }

    void setSizeInternal(unsigned size)
    {
      if (!SlaveTo)
	NumberOf = size;
      
      if (Contents != NULL)
	free(Contents);

      if (size == 0 || Unit == 0)
	Contents = NULL;
      else
      {
	Contents = new ElementT[Unit*size];
	if (Contents == NULL)
	  throw std::bad_alloc();
      }

      tSizeChangeNotifier::setSize(size);
    }

    /** Set the unit size of the array and reallocate the foreign array.
     */
    void setUnit(unsigned unit)
    {
      if (unit != Unit)
      {
        Unit = unit;
        setSizeInternal(NumberOf);
      }
    }

    /** Set the unit size of the array without reallocating. It is assumed
     * that the correct amount of memory has already been allocated.
     */
    void fixUnit(unsigned unit)
    {
      Unit = unit;
    }

    ElementT &get(unsigned index)
    {
      if (index >= NumberOf * Unit)
	throw std::runtime_error("index out of bounds");
      if (!Contents)
	throw std::runtime_error("Array unallocated");
      return Contents[ index ];
    }

    ElementT &getSub(unsigned index, unsigned sub_index)
    {
      return get(index * Unit + sub_index);
    }
};





template<class ElementT> 
class tForeignArray : public tReadOnlyForeignArray<ElementT>
{
    typedef tReadOnlyForeignArray<ElementT> super;

  public:
    tForeignArray(
        ElementT *&cts, int &number_of, unsigned unit=1, 
        tSizeChangeNotifier *slave_to=NULL,
        bool assume_ownership=false)
      : super(cts, number_of, unit, slave_to, assume_ownership)
    {
    }

    void set(unsigned index, ElementT value)
    {
      if (index >= this->NumberOf * this->Unit)
	throw std::runtime_error("index out of bounds");
      if (!this->Contents)
	throw std::runtime_error("Array unallocated");
      this->Contents[ index ] = value;
    }

    void setSub(unsigned index, unsigned sub_index, ElementT value)
    {
      set(index * this->Unit + sub_index, value);
    }

    tForeignArray &operator=(tForeignArray const &src)
    {
      if (this->SlaveTo)
        assert(src.size() == this->SlaveTo->size());
      else
        this->setSize(src.size());

      this->setUnit(src.Unit);

      if (src.Contents)
        memcpy(this->Contents, src.Contents, sizeof(ElementT) * this->Unit * src.size());
      else
        this->deallocate();

      return *this;
    }
};




#endif
